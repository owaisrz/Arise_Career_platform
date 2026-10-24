from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.risk_engine import analyze_job_listing
from backend.app.services.scam_eval_service import run_scam_model_evaluation

router = APIRouter(prefix="/assessments", tags=["Job Trust & Scam Risk"])

class EvaluateJobRequest(BaseModel):
    title: str
    employer: str
    description: str
    employer_domain: Optional[str] = ""
    contact_email: Optional[str] = ""
    contact_messaging: Optional[str] = ""
    salary_text: Optional[str] = ""
    application_url: Optional[str] = ""

@router.post("/evaluate")
async def evaluate_job_listing(req: EvaluateJobRequest):
    result = analyze_job_listing(
        title=req.title,
        employer=req.employer,
        description=req.description,
        employer_domain=req.employer_domain or "",
        contact_email=req.contact_email or "",
        contact_messaging=req.contact_messaging or "",
        salary_text=req.salary_text or "",
        application_url=req.application_url or ""
    )
    return result

@router.get("/benchmark")
async def get_scam_evaluation_benchmark():
    benchmark_results = run_scam_model_evaluation()
    return benchmark_results
