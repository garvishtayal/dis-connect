from fastapi import APIRouter

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateContentRequest,
    PreferencesRequest,
    PreferencesResponse,
    UnderstandSoulRequest,
    UnderstandSoulResponse,
)
from app.models.content import ContentItem, GenerateContentResponse
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


# Generate content items (query + scrape + mix + rank, return items).
@router.post("/agent/generate-content", response_model=GenerateContentResponse)
async def generate_content(req: GenerateContentRequest) -> GenerateContentResponse:
    items = await agent_service.generate_content(req)
    return GenerateContentResponse(items=items)


# Chat: LLM reply and needs_new_content flag.
@router.post("/agent/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    return agent_service.chat(req)


# Update content preferences via LLM.
@router.post("/agent/prefrences", response_model=PreferencesResponse)
def preferences(req: PreferencesRequest) -> PreferencesResponse:
    return agent_service.preferences(req)
