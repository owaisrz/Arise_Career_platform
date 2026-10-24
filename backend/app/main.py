from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1 import (
    auth,
    profile,
    documents,
    jobs,
    assessments,
    career_plans,
    applications,
    interviews,
    resumes,
    reports,
    fairness,
    dashboard,
    audit
)
from backend.app.seed_data import seed_initial_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed sample demonstration data if empty
    await seed_initial_data()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Careerloom — AI-Powered Evidence-Based Career Intelligence Platform for IMPACTX 2026",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(profile.router, prefix=api_v1_prefix)
app.include_router(documents.router, prefix=api_v1_prefix)
app.include_router(jobs.router, prefix=api_v1_prefix)
app.include_router(assessments.router, prefix=api_v1_prefix)
app.include_router(career_plans.router, prefix=api_v1_prefix)
app.include_router(applications.router, prefix=api_v1_prefix)
app.include_router(interviews.router, prefix=api_v1_prefix)
app.include_router(resumes.router, prefix=api_v1_prefix)
app.include_router(reports.router, prefix=api_v1_prefix)
app.include_router(fairness.router, prefix=api_v1_prefix)
app.include_router(dashboard.router, prefix=api_v1_prefix)
app.include_router(audit.router, prefix=api_v1_prefix)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to Careerloom API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }
