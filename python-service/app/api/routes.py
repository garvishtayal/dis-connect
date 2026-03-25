from fastapi import APIRouter

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateContentRequest,
    PreferencesRequest,
    PreferencesResponse,
    Query,
    UnderstandSoulRequest,
    UnderstandSoulResponse,
)
from app.services import agent_service

router = APIRouter()


# Health check for the agent service.
@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Understand user's initial soul prompt.
@router.post("/agent/understand-soul", response_model=UnderstandSoulResponse)
async def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    return agent_service.understand_soul(req)


# Generate LLM search queries — Go workers execute the scraping.
@router.post("/agent/generate-queries", response_model=list[Query])
def generate_queries(req: GenerateContentRequest) -> list[Query]:
    return agent_service.generate_queries(req)


# Chat: LLM reply and needs_new_content flag.
@router.post("/agent/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    return agent_service.chat(req)


# Update content preferences via LLM.
@router.post("/agent/prefrences", response_model=PreferencesResponse)
def preferences(req: PreferencesRequest) -> PreferencesResponse:
    return agent_service.preferences(req)
