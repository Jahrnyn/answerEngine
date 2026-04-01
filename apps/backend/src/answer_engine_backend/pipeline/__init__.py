"""Pipeline execution package for the Answer Engine backend."""

__all__ = ["RunExecutor"]


def __getattr__(name: str):
    if name == "RunExecutor":
        from answer_engine_backend.pipeline.executor import RunExecutor

        return RunExecutor
    raise AttributeError(name)
