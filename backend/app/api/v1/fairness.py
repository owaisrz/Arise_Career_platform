from fastapi import APIRouter
from backend.app.services.fairness_service import run_counterfactual_fairness_audit

router = APIRouter(prefix="/fairness", tags=["Fairness & Transparency"])

@router.get("/audit")
async def get_fairness_audit():
    audit_results = run_counterfactual_fairness_audit()
    return audit_results
