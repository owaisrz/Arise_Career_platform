from typing import List, Dict, Any

SKILL_PREREQUISITES: Dict[str, List[str]] = {
    "FastAPI": ["Python", "REST APIs"],
    "React": ["JavaScript", "HTML/CSS"],
    "TypeScript": ["JavaScript"],
    "Kubernetes": ["Docker", "Linux"],
    "Scikit-Learn": ["Python", "Pandas", "NumPy"],
    "PostgreSQL": ["SQL"],
    "CI/CD": ["Git", "Linux"],
    "Tailwind CSS": ["HTML/CSS"],
    "Docker": ["Linux"],
    "Pandas": ["Python"],
}

SKILL_PRACTICE_PROJECTS: Dict[str, Dict[str, str]] = {
    "Docker": {
        "title": "Containerize a Multi-Service App with Docker Compose",
        "description": "Write a multi-stage Dockerfile for a FastAPI backend and a React frontend, orchestration via docker-compose with health checks.",
        "duration": "4-6 hours",
        "evidence_type": "GitHub Repository + Docker Hub Tag"
    },
    "Kubernetes": {
        "title": "Local Kube Cluster Deployment with Minikube",
        "description": "Author Kubernetes manifests (Deployments, Services, ConfigMaps, Ingress) and deploy a sample service locally.",
        "duration": "6-8 hours",
        "evidence_type": "Kubernetes YAML manifests in Git"
    },
    "TypeScript": {
        "title": "Type-Safe Full-Stack API Contract",
        "description": "Refactor a JavaScript React client to strict TypeScript with Zod schemas and typed API client interfaces.",
        "duration": "3-5 hours",
        "evidence_type": "PR diff showing 100% strict type coverage"
    },
    "FastAPI": {
        "title": "Asynchronous REST API with Pydantic & SQLAlchemy",
        "description": "Build an authenticated microservice with async database queries, OpenAPI docs, and 90%+ pytest test coverage.",
        "duration": "5-7 hours",
        "evidence_type": "Working API endpoint tests & Swagger docs"
    },
    "PostgreSQL": {
        "title": "Relational Schema Design & Query Optimization",
        "description": "Construct normalized tables with foreign keys, index optimization, and write complex JOIN queries with EXPLAIN ANALYZE.",
        "duration": "3-4 hours",
        "evidence_type": "SQL migration script & query plan analysis"
    },
    "React": {
        "title": "Interactive Glassmorphism Dashboard Component",
        "description": "Build responsive glass-panel UI widgets with dynamic state, accessible keyboard navigation, and chart visualizer.",
        "duration": "4-6 hours",
        "evidence_type": "Live demo link & component code"
    },
    "Python": {
        "title": "Evidence Extraction & Parser Utility",
        "description": "Implement a deterministic parsing script that extracts structured entities and verbatim excerpts from text.",
        "duration": "3-5 hours",
        "evidence_type": "Python script & unit tests"
    },
    "Git": {
        "title": "Conventional Commits & Semantic Release Workflow",
        "description": "Configure GitHub branch protection rules, squash merging, and automate semantic version tagging.",
        "duration": "2-3 hours",
        "evidence_type": "Repository commit history"
    }
}

def analyze_skill_gaps(
    candidate_skills: List[Dict[str, Any]],
    job_required_skills: List[str],
    job_preferred_skills: List[str]
) -> Dict[str, Any]:
    cand_map = {}
    for s in candidate_skills:
        name = s.get("canonical_name", s.get("skill_name", "")).strip()
        cand_map[name.lower()] = s

    gaps = []
    demonstrated = []
    partially_supported = []

    all_target_skills = [(s, True) for s in job_required_skills] + [(s, False) for s in job_preferred_skills]
    
    for skill_name, is_required in all_target_skills:
        clean_name = skill_name.lower().strip()
        if clean_name in cand_map:
            cand_item = cand_map[clean_name]
            v_status = cand_item.get("verified_status", "self_reported")
            if v_status in ["project_verified", "document_extracted"]:
                demonstrated.append({
                    "skill": skill_name,
                    "proficiency": cand_item.get("proficiency_level", "Intermediate"),
                    "is_required": is_required,
                    "verified_status": v_status
                })
            else:
                partially_supported.append({
                    "skill": skill_name,
                    "proficiency": cand_item.get("proficiency_level", "Intermediate"),
                    "is_required": is_required,
                    "verified_status": v_status,
                    "gap_note": "Self-reported; lacking concrete project or assessment evidence."
                })
        else:
            # Missing skill - evaluate prerequisites
            prereqs = SKILL_PREREQUISITES.get(skill_name, [])
            missing_prereqs = [p for p in prereqs if p.lower() not in cand_map]
            practice_info = SKILL_PRACTICE_PROJECTS.get(skill_name, {
                "title": f"Build a Hands-on Project Demonstrating {skill_name}",
                "description": f"Create an open-source project or tutorial applying {skill_name} in a practical scenario.",
                "duration": "4-6 hours",
                "evidence_type": "Public GitHub Repository"
            })
            
            gaps.append({
                "skill": skill_name,
                "is_required": is_required,
                "priority": "High" if is_required else "Medium",
                "prerequisites": prereqs,
                "missing_prerequisites": missing_prereqs,
                "recommended_project": practice_info
            })

    # Sort gaps: required skills first, then by missing prerequisite count
    gaps.sort(key=lambda g: (0 if g["is_required"] else 1, len(g["missing_prerequisites"])))

    return {
        "demonstrated_skills": demonstrated,
        "partially_supported_skills": partially_supported,
        "skill_gaps": gaps,
        "total_gaps": len(gaps),
        "total_demonstrated": len(demonstrated)
    }
