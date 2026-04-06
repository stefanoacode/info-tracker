from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import init_db
from backend.scheduler import create_scheduler
from backend.seed import seed_database
from backend.api.people import router as people_router
from backend.api.feed import router as feed_router
from backend.api.trends import router as trends_router
from backend.api.digest import router as digest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Seed preset data
    sync_url = settings.database_url.replace("+aiosqlite", "")
    engine = create_engine(sync_url)
    with Session(engine) as db:
        seed_database(db)

    scheduler = create_scheduler(interval_hours=settings.collection_interval_hours)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Info Tracker", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(people_router, prefix="/api")
app.include_router(feed_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(digest_router, prefix="/api")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
