import json
from queue import Queue
from threading import Thread

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from answer_engine_backend.cfhee_client import CfheeClientError
from answer_engine_backend.model_runtime import ModelRuntimeError
from answer_engine_backend.pipeline import RunExecutor
from answer_engine_backend.pipeline.models import AnswerRun, ExecuteRunRequest, RunEvent, utc_now


router = APIRouter(prefix="/runs", tags=["runs"])
run_executor = RunExecutor()


@router.post("/execute", response_model=AnswerRun)
def execute_run(request: ExecuteRunRequest) -> AnswerRun:
    try:
        return run_executor.execute(request.query)
    except CfheeClientError as error:
        raise HTTPException(status_code=error.status_code, detail=error.to_detail()) from error
    except ModelRuntimeError as error:
        raise HTTPException(status_code=error.status_code, detail=error.to_detail()) from error


@router.post("/stream")
def stream_run(request: ExecuteRunRequest) -> StreamingResponse:
    event_queue: Queue[RunEvent | None] = Queue()
    run_id_holder: dict[str, str | None] = {"run_id": None}

    def push_event(event: RunEvent) -> None:
        run_id_holder["run_id"] = event.run_id
        event_queue.put(event)

    def run_in_background() -> None:
        try:
            run_executor.execute(request.query, event_sink=push_event)
        except (CfheeClientError, ModelRuntimeError) as error:
            push_event(
                RunEvent(
                    run_id=run_id_holder["run_id"] or "run-uninitialized",
                    event_type="run_failed",
                    stage_id=None,
                    timestamp=utc_now(),
                    message=error.message,
                    summary={
                        "category": error.to_detail().get("category"),
                        "endpoint": error.to_detail().get("endpoint"),
                    },
                )
            )
        except Exception as error:  # pragma: no cover - defensive terminal path
            push_event(
                RunEvent(
                    run_id=run_id_holder["run_id"] or "run-uninitialized",
                    event_type="run_failed",
                    stage_id=None,
                    timestamp=utc_now(),
                    message=str(error),
                    summary={"category": "unexpected_failure"},
                )
            )
        finally:
            event_queue.put(None)

    def event_stream():
        worker = Thread(target=run_in_background, daemon=True)
        worker.start()

        while True:
            event = event_queue.get()
            if event is None:
                break
            yield _serialize_sse_event(event)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _serialize_sse_event(event: RunEvent) -> str:
    payload = json.dumps(event.model_dump(mode="json"))
    return f"event: {event.event_type}\ndata: {payload}\n\n"
