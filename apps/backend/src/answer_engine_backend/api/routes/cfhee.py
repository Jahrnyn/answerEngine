from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from answer_engine_backend.cfhee_client import CfheeClient, CfheeClientError
from answer_engine_backend.settings import get_settings


router = APIRouter(prefix="/cfhee", tags=["cfhee"])


class RetrievalQueryRequest(BaseModel):
    query: str = Field(min_length=1)
    scope: dict
    top_k: int = 5
    include_chunks: bool = True


def get_cfhee_client() -> CfheeClient:
    return CfheeClient(get_settings())


def _raise_http_error(error: CfheeClientError) -> None:
    raise HTTPException(status_code=error.status_code, detail=error.to_detail()) from error


@router.get("/health")
def get_cfhee_health() -> dict:
    try:
        return get_cfhee_client().get_health()
    except CfheeClientError as error:
        _raise_http_error(error)


@router.get("/capabilities")
def get_cfhee_capabilities() -> dict:
    try:
        return get_cfhee_client().get_capabilities()
    except CfheeClientError as error:
        _raise_http_error(error)


@router.get("/scopes/values")
def get_cfhee_scope_values() -> dict:
    try:
        return get_cfhee_client().get_scope_values()
    except CfheeClientError as error:
        _raise_http_error(error)


@router.get("/scopes/tree")
def get_cfhee_scope_tree() -> dict:
    try:
        return get_cfhee_client().get_scope_tree()
    except CfheeClientError as error:
        _raise_http_error(error)


@router.post("/retrieval/query")
def post_cfhee_retrieval_query(request: RetrievalQueryRequest) -> dict:
    try:
        return get_cfhee_client().query_retrieval(request.model_dump())
    except CfheeClientError as error:
        _raise_http_error(error)
