import json
from typing import Dict, List, Any

def generate_tailored_resume_content(
    profile_data: Dict[str, Any],
    selected_project_ids: List[str],
    selected_skills: List[str],
    is_redacted: bool = False,
    redacted_fields: List[str] = None
) -> Dict[str, Any]:
    redacted_fields = redacted_fields or ["phone", "email"]
    
    full_name = profile_data.get("full_name", "Candidate")
    email = profile_data.get("email", "")
    phone = profile_data.get("phone", "")
    headline = profile_data.get("headline", "")
    summary = profile_data.get("summary", "")
    
    if is_redacted:
        if "full_name" in redacted_fields:
            full_name = "Candidate [Identified upon NDA/Consent]"
        if "email" in redacted_fields:
            email = "[Contact via Careerloom Secure Relay]"
        if "phone" in redacted_fields:
            phone = "[Phone Redacted for Privacy]"

    # Filter projects
    all_projects = profile_data.get("projects", [])
    if selected_project_ids:
        filtered_projects = [p for p in all_projects if p.get("id") in selected_project_ids]
    else:
        filtered_projects = all_projects

    # Filter skills
    all_skills = profile_data.get("skills", [])
    if selected_skills:
        filtered_skills = [s for s in all_skills if s.get("canonical_name", s.get("skill_name")) in selected_skills]
    else:
        filtered_skills = all_skills

    return {
        "header": {
            "name": full_name,
            "email": email,
            "phone": phone,
            "headline": headline,
            "portfolio_url": profile_data.get("portfolio_url", ""),
            "github_url": profile_data.get("github_url", ""),
            "is_redacted": is_redacted,
            "redacted_fields": redacted_fields
        },
        "summary": summary,
        "skills": filtered_skills,
        "projects": filtered_projects,
        "education": profile_data.get("education", []),
        "work_experience": profile_data.get("work_experience", [])
    }
