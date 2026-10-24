from typing import List, Dict, Any

def generate_30_day_plan_tasks(
    target_role: str,
    skill_gaps: List[Dict[str, Any]],
    target_job_title: str = ""
) -> List[Dict[str, Any]]:
    tasks = []
    
    top_gap_skills = [g["skill"] for g in skill_gaps[:3]] if skill_gaps else ["Docker", "TypeScript", "FastAPI"]
    primary_gap = top_gap_skills[0] if len(top_gap_skills) > 0 else "Advanced System Design"
    secondary_gap = top_gap_skills[1] if len(top_gap_skills) > 1 else "Testing & Automation"
    tertiary_gap = top_gap_skills[2] if len(top_gap_skills) > 2 else "Cloud Deployment"

    # Stage 1: Days 1–7 (Assess and Prioritize)
    tasks.append({
        "stage": "Days 1–7: Assess and prioritize",
        "day_number": 1,
        "title": f"Profile & Evidence Audit for {target_role}",
        "description": "Upload latest resume to Careerloom Document Scanner, review extracted claims, and approve verified project links.",
        "linked_skill": "Career Management",
        "priority": "High",
        "duration_hours": 2,
        "due_date": "Day 1"
    })
    tasks.append({
        "stage": "Days 1–7: Assess and prioritize",
        "day_number": 3,
        "title": f"Deep Dive into {primary_gap} Architecture & Core Principles",
        "description": f"Study official documentation and architectural patterns for {primary_gap}. Note fundamental concepts and common interview pitfalls.",
        "linked_skill": primary_gap,
        "priority": "High",
        "duration_hours": 3,
        "due_date": "Day 3"
    })
    tasks.append({
        "stage": "Days 1–7: Assess and prioritize",
        "day_number": 5,
        "title": f"Setup Development Environment for {primary_gap}",
        "description": f"Configure local toolchain, linters, and sample starter template for {primary_gap} hands-on development.",
        "linked_skill": primary_gap,
        "priority": "Medium",
        "duration_hours": 2,
        "due_date": "Day 5"
    })
    tasks.append({
        "stage": "Days 1–7: Assess and prioritize",
        "day_number": 7,
        "title": "Evaluate 5 Target Job Listings on Job Trust Checker",
        "description": "Run job postings through Careerloom Scam & Risk Assessment. Filter out listings with suspicious payment or communication signals.",
        "linked_skill": "Research & Evaluation",
        "priority": "High",
        "duration_hours": 2,
        "due_date": "Day 7"
    })

    # Stage 2: Days 8–14 (Learn and Build Evidence)
    tasks.append({
        "stage": "Days 8–14: Learn and build evidence",
        "day_number": 8,
        "title": f"Build Hands-on Milestone 1: {primary_gap} Implementation",
        "description": f"Develop core functional components for a real-world project demonstrating practical competence in {primary_gap}.",
        "linked_skill": primary_gap,
        "priority": "High",
        "duration_hours": 4,
        "due_date": "Day 8"
    })
    tasks.append({
        "stage": "Days 8–14: Learn and build evidence",
        "day_number": 10,
        "title": f"Implement Automated Tests for {primary_gap} Project",
        "description": "Write comprehensive unit and integration tests with >80% code coverage to substantiate technical rigor.",
        "linked_skill": primary_gap,
        "priority": "High",
        "duration_hours": 3,
        "due_date": "Day 10"
    })
    tasks.append({
        "stage": "Days 8–14: Learn and build evidence",
        "day_number": 12,
        "title": f"Exploratory Lab: {secondary_gap} Integration",
        "description": f"Connect your primary project with {secondary_gap}. Document API contracts and data flows in README.",
        "linked_skill": secondary_gap,
        "priority": "Medium",
        "duration_hours": 3,
        "due_date": "Day 12"
    })
    tasks.append({
        "stage": "Days 8–14: Learn and build evidence",
        "day_number": 14,
        "title": "Publish Project to GitHub with Architectural Diagram",
        "description": "Write clean documentation, deploy live demo if applicable, and attach repository URL to Careerloom profile evidence.",
        "linked_skill": "Technical Communication",
        "priority": "High",
        "duration_hours": 2,
        "due_date": "Day 14"
    })

    # Stage 3: Days 15–21 (Apply Strategically)
    tasks.append({
        "stage": "Days 15–21: Apply strategically",
        "day_number": 15,
        "title": "Create Tailored Employer-Specific Resumes in Resume Studio",
        "description": f"Generate customized resume versions highlighting {primary_gap} evidence for your top 3 target employers.",
        "linked_skill": "Resume Optimization",
        "priority": "High",
        "duration_hours": 2,
        "due_date": "Day 15"
    })
    tasks.append({
        "stage": "Days 15–21: Apply strategically",
        "day_number": 17,
        "title": "Configure Consent & Privacy Controls for Shared Resumes",
        "description": "Select contact redaction preferences and verify employer share tokens on Careerloom sharing ledger.",
        "linked_skill": "Data Privacy",
        "priority": "Medium",
        "duration_hours": 1,
        "due_date": "Day 17"
    })
    tasks.append({
        "stage": "Days 15–21: Apply strategically",
        "day_number": 19,
        "title": "Submit 3 High-Match Applications & Log in Pipeline Tracker",
        "description": "Apply directly on verified employer portals and record application status, resume version, and dates in Kanban tracker.",
        "linked_skill": "Application Strategy",
        "priority": "High",
        "duration_hours": 3,
        "due_date": "Day 19"
    })
    tasks.append({
        "stage": "Days 15–21: Apply strategically",
        "day_number": 21,
        "title": "Network Outreach with 2 Verified Practitioners",
        "description": f"Engage with engineers working in {target_role} roles. Ask thoughtful questions about day-to-day challenges.",
        "linked_skill": "Professional Networking",
        "priority": "Medium",
        "duration_hours": 2,
        "due_date": "Day 21"
    })

    # Stage 4: Days 22–30 (Prepare and Improve)
    tasks.append({
        "stage": "Days 22–30: Prepare and improve",
        "day_number": 23,
        "title": f"Practice {primary_gap} Technical Interview Questions",
        "description": "Complete 3 technical coding and architectural questions in Careerloom Interview Studio and review rubrics.",
        "linked_skill": primary_gap,
        "priority": "High",
        "duration_hours": 3,
        "due_date": "Day 23"
    })
    tasks.append({
        "stage": "Days 22–30: Prepare and improve",
        "day_number": 25,
        "title": "Structure STAR Stories for Behavioral Interview Scenarios",
        "description": "Formulate 4 concrete STAR (Situation, Task, Action, Result) narratives grounded in your real project history.",
        "linked_skill": "Behavioral Interviewing",
        "priority": "High",
        "duration_hours": 2,
        "due_date": "Day 25"
    })
    tasks.append({
        "stage": "Days 22–30: Prepare and improve",
        "day_number": 28,
        "title": "Simulated Mock Technical Interview Session",
        "description": "Conduct a timed practice interview in Interview Studio, type complete answers, and evaluate rubric feedback.",
        "linked_skill": "Interview Execution",
        "priority": "High",
        "duration_hours": 3,
        "due_date": "Day 28"
    })
    tasks.append({
        "stage": "Days 22–30: Prepare and improve",
        "day_number": 30,
        "title": "30-Day Progress Retrospective & Next Cycle Planning",
        "description": "Review completed tasks, assess new project evidence added, and recalibrate match scores against active market jobs.",
        "linked_skill": "Continuous Improvement",
        "priority": "Medium",
        "duration_hours": 2,
        "due_date": "Day 30"
    })

    return tasks
