from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.llm.client import LLMError


def _detail(msg: str, max_len: int = 500) -> str:
    return (msg[:max_len] + "…") if len(msg) > max_len else msg


async def on_llm_error(_: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": _detail(str(exc))})


async def on_value_error(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def on_runtime_error(_: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": _detail(str(exc))})


async def on_exception(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def create_app() -> FastAPI:
    app = FastAPI(title="dis-connect Python Agent")
    app.include_router(api_router)
    app.add_exception_handler(LLMError, on_llm_error)
    app.add_exception_handler(ValueError, on_value_error)
    app.add_exception_handler(RuntimeError, on_runtime_error)
    app.add_exception_handler(Exception, on_exception)
    return app


app = create_app()

