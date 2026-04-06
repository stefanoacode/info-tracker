import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.collectors.rss import RSSCollector
from backend.collectors.reddit import RedditCollector
from backend.collectors.youtube import YouTubeCollector
from backend.collectors.twitter import TwitterCollector
from backend.config import settings
from backend.llm.claude_provider import ClaudeProvider
from backend.services.collector_service import CollectorService
from backend.services.summarizer import SummarizerService
from backend.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)

def _get_sync_db() -> Session:
    sync_url = settings.database_url.replace("+aiosqlite", "")
    engine = create_engine(sync_url)
    return Session(engine)

def _get_collectors() -> dict:
    collectors = {"substack": RSSCollector(), "reddit": RedditCollector()}
    if settings.youtube_api_key:
        collectors["youtube"] = YouTubeCollector(api_key=settings.youtube_api_key)
    if settings.x_api_bearer_token:
        collectors["x"] = TwitterCollector(bearer_token=settings.x_api_bearer_token)
    return collectors

async def run_collection_job():
    logger.info("Starting scheduled collection...")
    db = _get_sync_db()
    try:
        service = CollectorService(collectors=_get_collectors())
        new_content = await service.collect_all(db)
        logger.info(f"Collected {len(new_content)} new items")
    finally:
        db.close()

async def run_summarization_job():
    logger.info("Starting scheduled summarization...")
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key configured, skipping summarization")
        return
    db = _get_sync_db()
    try:
        llm = ClaudeProvider(api_key=settings.anthropic_api_key)
        service = SummarizerService(llm=llm)
        count = await service.summarize_pending(db)
        logger.info(f"Summarized {count} items")
    finally:
        db.close()

async def run_trend_analysis_job():
    logger.info("Starting scheduled trend analysis...")
    if not settings.anthropic_api_key:
        return
    db = _get_sync_db()
    try:
        llm = ClaudeProvider(api_key=settings.anthropic_api_key)
        service = AnalyticsService(llm=llm)
        trends = await service.detect_trends(db)
        logger.info(f"Detected {len(trends)} trends")
    finally:
        db.close()

def create_scheduler(interval_hours: int = 6) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_collection_job, "interval", hours=interval_hours, id="collection")
    scheduler.add_job(run_summarization_job, "interval", hours=interval_hours, minutes=15, id="summarization")
    scheduler.add_job(run_trend_analysis_job, "interval", hours=24, id="trends")
    return scheduler
