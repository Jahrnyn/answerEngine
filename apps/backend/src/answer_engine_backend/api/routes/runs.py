from fastapi import APIRouter, HTTPException

from answer_engine_backend.cfhee_client import CfheeClientError
from answer_engine_backend.model_runtime import ModelRuntimeError
from answer_engine_backend.pipeline import RunExecutor
from answer_engine_backend.pipeline.models import AnswerRun, ExecuteRunRequest


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
