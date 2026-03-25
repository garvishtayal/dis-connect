"""Scraper endpoints called by Go workers. No auth — internal service only."""
from fastapi import APIRouter
from pydantic import BaseModel

from app.models.content import ContentItem
from app.services import scraper_service

router = APIRouter(prefix="/scraper")


class YouTubeScrapeRequest(BaseModel):
    query: str


class PinterestScrapeRequest(BaseModel):
    query: str
    proxy: str = ""


@router.post("/youtube", response_model=list[ContentItem])
async def scrape_youtube(req: YouTubeScrapeRequest) -> list[ContentItem]:
    return await scraper_service.scrape_youtube(req.query)


@router.post("/pinterest", response_model=list[ContentItem])
async def scrape_pinterest(req: PinterestScrapeRequest) -> list[ContentItem]:
    return await scraper_service.scrape_pinterest(req.query, req.proxy)
