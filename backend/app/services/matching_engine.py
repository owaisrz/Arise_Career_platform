import json
from typing import Dict, List, Any

def compute_job_match(
    candidate_skills: List[Dict[str, Any]],
    candidate_projects: List[Dict[str, Any]],
    candidate_experience: List[Dict[str, Any]],
    required_skills: List[str],
    preferred_skills: List[str],
    job_experience_required: str = "1-3 years",
    work_arrangement: str = "remote",
    candidate_arrangement_pref: str = "remote"
) -> Dict[str, Any]:
    # Normalize candidate skills
    candidate_skill_map = {}
    for s in candidate_skills:
        canonical = s.get("canonical_name", s.get("skill_name", "")).lower().strip()
        candidate_skill_map[canonical] = s

    # Collect skills demonstrated in projects
    project_skill_set = set()
    for p in candidate_projects:
        skills_raw = p.get("skills_used", "[]")
        if isinstance(skills_raw, str):
            try:
                p_skills = json.loads(skills_raw)
            except Exception:
                p_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
        else:
            p_skills = skills_raw or []
        for ps in p_skills:
            project_skill_set.add(ps.lower().strip())

    # Evaluate required skills
    matched_required = []
    missing_required = []
    for req in required_skills:
        req_clean = req.lower().strip()
        if req_clean in candidate_skill_map:
            cand_skill = candidate_skill_map[req_clean]
            # Check if supported by project evidence
            has_project_evidence = req_clean in project_skill_set
            matched_required.append({
                "skill": req,
                "proficiency": cand_skill.get("proficiency_level", "Intermediate"),
                "verified_status": "project_verified" if has_project_evidence else cand_skill.get("verified_status", "self_reported"),
                "supported_by_project": has_project_evidence,
                "evidence_excerpt": f"Demonstrated in verified candidate project" if has_project_evidence else "Reported in candidate profile"
            })
        else:
            missing_required.append(req)

    # Evaluate preferred skills
    matched_preferred = []
    missing_preferred = []
    for pref in preferred_skills:
        pref_clean = pref.lower().strip()
        if pref_clean in candidate_skill_map:
            cand_skill = candidate_skill_map[pref_clean]
            has_project_evidence = pref_clean in project_skill_set
            matched_preferred.append({
                "skill": pref,
                "proficiency": cand_skill.get("proficiency_level", "Intermediate"),
                "verified_status": "project_verified" if has_project_evidence else cand_skill.get("verified_status", "self_reported"),
                "supported_by_project": has_project_evidence
            })
        else:
            missing_preferred.append(pref)

    # Score components
    req_ratio = len(matched_required) / max(1, len(required_skills)) if required_skills else 1.0
    pref_ratio = len(matched_preferred) / max(1, len(preferred_skills)) if preferred_skills else 0.5
    
    # Project evidence alignment
    project_evidence_count = sum(1 for m in matched_required if m["supported_by_project"])
    evidence_ratio = project_evidence_count / max(1, len(required_skills)) if required_skills else 0.8
    
    # Work arrangement alignment
    arrangement_fit = 1.0 if (work_arrangement.lower() == "remote" or candidate_arrangement_pref.lower() == work_arrangement.lower()) else 0.7

    # Weighted calculation
    # 50% Required Skills, 20% Preferred Skills, 20% Verified Project Evidence, 10% Work arrangement fit
    req_score = req_ratio * 50.0
    pref_score = pref_ratio * 20.0
    evidence_score = evidence_ratio * 20.0
    arrangement_score = arrangement_fit * 10.0
    
    total_match = req_score + pref_score + evidence_score + arrangement_score
    final_score = round(min(100.0, max(10.0, total_match)), 1)

    # Compile actionable skills to improve
    skills_to_improve = missing_required[:4] + missing_preferred[:2]

    explanation = {
        "summary": f"Matches {len(matched_required)} of {len(required_skills)} required skills, with {project_evidence_count} supported by tangible project evidence.",
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "skills_to_improve": skills_to_improve,
        "scoring_weights": {
            "required_skills_weight": "50%",
            "preferred_skills_weight": "20%",
            "verified_evidence_weight": "20%",
            "arrangement_fit_weight": "10%"
        },
        "score_breakdown": {
            "required_skills_score": round(req_score, 1),
            "preferred_skills_score": round(pref_score, 1),
            "evidence_score": round(evidence_score, 1),
            "arrangement_score": round(arrangement_score, 1)
        },
        "fairness_note": "Score is derived strictly from observable skill and project evidence. No demographic, university pedigree, or geographic proxies were utilized.",
        "disclaimer": "This score indicates evidence alignment with the stated job requirements; it is not a guarantee of interview selection or employment."
    }

    return {
        "match_score": final_score,
        "required_skills_score": round(req_score, 1),
        "preferred_skills_score": round(pref_score, 1),
        "experience_score": round(evidence_score, 1),
        "explanation": explanation
    }
