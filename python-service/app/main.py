from fastapi import FastAPI

from app.api.routes import router as api_router


# Builds the FastAPI application and wires API routes.
def create_app() -> FastAPI:
    app = FastAPI(title="dis-connect Python Agent")
    app.include_router(api_router)
    return app


app = create_app()

