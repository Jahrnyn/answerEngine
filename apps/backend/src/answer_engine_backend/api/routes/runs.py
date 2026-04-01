from fastapi import APIRouter

from answer_engine_backend.pipeline import RunExecutor
from answer_engine_backend.pipeline.models import AnswerRun, ExecuteRunRequest


router = APIRouter(prefix="/runs", tags=["runs"])
run_executor = RunExecutor()


@router.post("/execute", response_model=AnswerRun)
def execute_run(request: ExecuteRunRequest) -> AnswerRun:
    return run_executor.execute(request.query)
