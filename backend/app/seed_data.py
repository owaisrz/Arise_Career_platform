import json
from datetime import datetime, timezone
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile, CandidateSkill, Project, Education, WorkExperience, SkillEvidence
from backend.app.models.job import JobListing, SavedJob
from backend.app.models.assessment import JobAssessment, RiskSignal
from backend.app.models.application import Application
from backend.app.models.career_plan import CareerPlan, CareerPlanTask
from backend.app.models.interview import InterviewSession, InterviewQuestion, InterviewPractice
from backend.app.models.report import AuditEvent
from backend.app.models.skill import SkillTaxonomy
from backend.app.services.risk_engine import analyze_job_listing
from backend.app.services.career_plan_service import generate_30_day_plan_tasks

async def seed_initial_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        user_res = await db.execute(select(User).where(User.email == "alex.morgan@careerloom.dev"))
        if user_res.scalar_one_or_none():
            return  # Already seeded

        # 1. Create Demo User: Alex Morgan
        demo_user = User(
            email="alex.morgan@careerloom.dev",
            hashed_password=get_password_hash("password123"),
            full_name="Alex Morgan",
            role="candidate"
        )
        db.add(demo_user)
        await db.flush()

        # 2. Candidate Profile
        profile = CandidateProfile(
            user_id=demo_user.id,
            headline="Junior Full Stack & Data Engineer | Evidence-Driven Technologist",
            summary="Early-career developer with hands-on project experience in Python, FastAPI, React, SQL, and Docker. Enthusiastic about creating transparent, accessible software with demonstrable engineering evidence.",
            preferred_role="Full Stack Software Engineer",
            preferred_location="Bangalore / Remote",
            work_arrangement="remote",
            availability="Immediate (2 weeks notice)",
            phone="+91 98765 43210",
            portfolio_url="https://alexmorgan.dev",
            github_url="https://github.com/alexmorgan-dev",
            linkedin_url="https://linkedin.com/in/alexmorgan-dev"
        )
        db.add(profile)
        await db.flush()

        # 3. Education
        edu = Education(
            profile_id=profile.id,
            institution="National Institute of Technology",
            degree="Bachelor of Technology in Computer Science",
            field_of_study="Computer Science & Engineering",
            start_year=2021,
            end_year=2025,
            grade="8.8 / 10.0 CGPA",
            is_extracted=True,
            source_reference="Verified Degree Transcript — Document ID: DOC-2025-01"
        )
        db.add(edu)

        # 4. Work Experience
        exp = WorkExperience(
            profile_id=profile.id,
            company="Horizon Digital Labs",
            role="Junior Web Developer Intern",
            location="Remote",
            start_date="Jun 2024",
            end_date="Dec 2024",
            is_current=False,
            description="Contributed to RESTful backend endpoints using Python FastAPI. Built responsive client-side UI dashboards with React and Tailwind CSS. Implemented automated pytest suites maintaining 88% test coverage.",
            is_extracted=True,
            source_reference="Internship Completion Letter — Verified"
        )
        db.add(exp)

        # 5. Projects
        p1 = Project(
            profile_id=profile.id,
            title="CloudMetrics — Real-Time Systems Telemetry Dashboard",
            description="Engineered an end-to-end monitoring service using FastAPI, async PostgreSQL, and React. Collects machine vitals and renders high-frequency charts with sub-100ms latency.",
            skills_used=json.dumps(["Python", "FastAPI", "SQL", "PostgreSQL", "React", "Docker"]),
            demo_url="https://cloudmetrics-demo.alexmorgan.dev",
            repo_url="https://github.com/alexmorgan-dev/cloudmetrics",
            role="Lead Developer",
            is_extracted=True,
            source_reference="GitHub Repository + Live Telemetry Demo"
        )
        p2 = Project(
            profile_id=profile.id,
            title="LoomUI — Crystal Glassmorphism Component Library",
            description="Designed and published an accessible, lightweight UI design kit featuring genuine backdrop-filter frosted glass surfaces, keyboard navigation, and WCAG AA contrast compliance.",
            skills_used=json.dumps(["React", "TypeScript", "Tailwind CSS", "HTML/CSS"]),
            demo_url="https://loomui.dev",
            repo_url="https://github.com/alexmorgan-dev/loomui",
            role="Creator & Maintainer",
            is_extracted=True,
            source_reference="Published Open Source NPM Library"
        )
        p3 = Project(
            profile_id=profile.id,
            title="SecCrawler — Automated Job Post Scam Classifier",
            description="Built a rule-based multi-signal evaluation script in Python to identify suspicious recruitment patterns, anachronistic technology requirements, and upfront payment demands.",
            skills_used=json.dumps(["Python", "Data Analysis", "REST APIs", "Git"]),
            demo_url="https://github.com/alexmorgan-dev/sec-crawler",
            repo_url="https://github.com/alexmorgan-dev/sec-crawler",
            role="Developer",
            is_extracted=True,
            source_reference="Independent Research Project"
        )
        db.add_all([p1, p2, p3])
        await db.flush()

        # 6. Candidate Skills & Evidence
        initial_skills = [
            ("Python", "Python", "Advanced", "Technical", "project_verified", 0.95),
            ("FastAPI", "FastAPI", "Intermediate", "Technical", "project_verified", 0.90),
            ("React", "React", "Advanced", "Technical", "project_verified", 0.92),
            ("TypeScript", "TypeScript", "Intermediate", "Technical", "project_verified", 0.88),
            ("SQL", "SQL", "Advanced", "Technical", "project_verified", 0.94),
            ("PostgreSQL", "PostgreSQL", "Intermediate", "Technical", "project_verified", 0.89),
            ("Tailwind CSS", "Tailwind CSS", "Advanced", "Technical", "project_verified", 0.92),
            ("Docker", "Docker", "Beginner", "DevOps", "self_reported", 0.70),
            ("Git", "Git", "Advanced", "DevOps", "project_verified", 0.95),
            ("HTML/CSS", "HTML/CSS", "Advanced", "Technical", "project_verified", 0.96),
        ]
        
        for name, canon, prof_lvl, cat, v_stat, conf in initial_skills:
            c_skill = CandidateSkill(
                profile_id=profile.id,
                skill_name=name,
                canonical_name=canon,
                proficiency_level=prof_lvl,
                category=cat,
                verified_status=v_stat,
                confidence_score=conf
            )
            db.add(c_skill)
            await db.flush()

            if v_stat == "project_verified":
                evi = SkillEvidence(
                    candidate_skill_id=c_skill.id,
                    evidence_type="project",
                    source_title=p1.title if name in ["Python", "FastAPI", "SQL", "PostgreSQL"] else p2.title,
                    excerpt=f"Substantiated by verified project repository commits and working live demo for {name}.",
                    confidence=conf,
                    is_approved=True
                )
                db.add(evi)

        # 7. Seed Job Listings
        jobs_to_seed = [
            {
                "title": "Junior Full Stack Engineer",
                "employer": "Meridian Health Technologies",
                "employer_domain": "meridianhealth.com",
                "location": "Bengaluru (Hybrid)",
                "work_arrangement": "hybrid",
                "salary_text": "₹8,50,000 - ₹11,00,000 / yr",
                "description": "Join our digital health platform team. You will build responsive React client interfaces, design resilient RESTful APIs in Python FastAPI, and optimize PostgreSQL queries. Requirements: Proficiency in Python and React, familiarity with relational databases, and a collaborative mindset. We conduct a structured 3-round interview.",
                "required_skills": ["Python", "React", "SQL", "FastAPI"],
                "preferred_skills": ["Docker", "TypeScript", "PostgreSQL"],
                "contact_email": "careers@meridianhealth.com"
            },
            {
                "title": "Frontend React & TypeScript Specialist",
                "employer": "Loomis Commerce Systems",
                "employer_domain": "loomiscommerce.com",
                "location": "Remote (Pan-India)",
                "work_arrangement": "remote",
                "salary_text": "$80,000 - $95,000",
                "description": "Develop high-performance digital commerce web applications. Build reusable crystal-clear design systems in React and TypeScript. Collaborate with product designers and backend engineers. Requirements: Strong experience in React, TypeScript, HTML/CSS, and modern frontend testing.",
                "required_skills": ["React", "TypeScript", "HTML/CSS", "Tailwind CSS"],
                "preferred_skills": ["Git", "REST APIs", "CI/CD"],
                "contact_email": "talent@loomiscommerce.com"
            },
            {
                "title": "Cloud Platform & DevOps Associate",
                "employer": "Astra Cloud Platforms",
                "employer_domain": "astracloud.io",
                "location": "Hyderabad / Remote",
                "work_arrangement": "remote",
                "salary_text": "₹10,00,000 - ₹14,00,000 / yr",
                "description": "Maintain Kubernetes clusters, containerize microservice architectures, and configure automated GitHub Actions CI/CD pipelines. Looking for motivated engineers with Linux and Docker fundamentals.",
                "required_skills": ["Docker", "Linux", "Git", "CI/CD"],
                "preferred_skills": ["Kubernetes", "Python", "AWS"],
                "contact_email": "recruiting@astracloud.io"
            },
            {
                "title": "Associate Data Analyst & Engineer",
                "employer": "Beacon Financial Analytics",
                "employer_domain": "beaconfinancial.org",
                "location": "Mumbai (Onsite)",
                "work_arrangement": "onsite",
                "salary_text": "₹7,50,000 - ₹9,50,000 / yr",
                "description": "Author analytical SQL transformations, clean transactional datasets using Python and pandas, and build automated reporting dashboards for investment teams.",
                "required_skills": ["SQL", "Python", "Data Analysis", "PostgreSQL"],
                "preferred_skills": ["FastAPI", "Git", "Tableau"],
                "contact_email": "analytics-jobs@beaconfinancial.org"
            },
            # Suspicious Job A: Payment demand
            {
                "title": "Virtual Data Entry & Document Clerk",
                "employer": "Apex Global Online",
                "employer_domain": "apex-jobportal.xyz",
                "location": "Remote",
                "work_arrangement": "remote",
                "salary_text": "$160/hr ($6,400/week)",
                "description": "Immediate hire guaranteed! Earn $160/hr doing simple typing and data entry from home. Before you can be assigned customer records, you must pay a processing fee of $75 to receive your dedicated security dongle and credentials.",
                "required_skills": ["Data Entry", "Microsoft Word"],
                "preferred_skills": [],
                "contact_email": "apexjobs@gmail.com"
            },
            # Suspicious Job B: Telegram only + Impossible Flutter timeline
            {
                "title": "Lead Mobile Flutter Developer",
                "employer": "Swift Mobility Labs",
                "employer_domain": "swiftmobility.top",
                "location": "Remote",
                "work_arrangement": "remote",
                "salary_text": "$150,000",
                "description": "We are seeking a senior lead with 12 years of experience in Flutter and Dart. Contact strictly via Telegram @swift_hiring_manager to claim your offer letter. No formal interview needed.",
                "required_skills": ["Flutter", "Dart", "Mobile"],
                "preferred_skills": [],
                "contact_email": "swiftrecruiter@outlook.com",
                "contact_messaging": "Telegram: @swift_hiring_manager"
            }
        ]

        saved_jobs_created = []
        for jd in jobs_to_seed:
            job = JobListing(
                title=jd["title"],
                employer=jd["employer"],
                employer_domain=jd["employer_domain"],
                location=jd["location"],
                work_arrangement=jd["work_arrangement"],
                salary_text=jd["salary_text"],
                description=jd["description"],
                required_skills=json.dumps(jd["required_skills"]),
                preferred_skills=json.dumps(jd["preferred_skills"]),
                contact_email=jd.get("contact_email", ""),
                contact_messaging=jd.get("contact_messaging", ""),
                source="seed_demo"
            )
            db.add(job)
            await db.flush()
            saved_jobs_created.append(job)

            # Analyze and persist risk assessment
            analysis = analyze_job_listing(
                title=job.title,
                employer=job.employer,
                description=job.description,
                employer_domain=job.employer_domain,
                contact_email=job.contact_email,
                contact_messaging=job.contact_messaging,
                salary_text=job.salary_text
            )
            assessment = JobAssessment(
                job_id=job.id,
                user_id=demo_user.id,
                risk_score=analysis["risk_score"],
                risk_tier=analysis["risk_tier"],
                summary=analysis["summary"],
                positive_signals=json.dumps(analysis["positive_signals"]),
                unknown_signals=json.dumps(analysis["unknown_signals"])
            )
            db.add(assessment)
            await db.flush()

            for s in analysis["signals"]:
                sig = RiskSignal(
                    assessment_id=assessment.id,
                    signal_category=s["signal_category"],
                    severity=s["severity"],
                    title=s["title"],
                    description=s["description"],
                    evidence_excerpt=s["evidence_excerpt"],
                    certainty=s["certainty"],
                    recommended_action=s["recommended_action"]
                )
                db.add(sig)

        # 8. Seed Applications across stages
        app1 = Application(
            user_id=demo_user.id,
            job_id=saved_jobs_created[0].id,  # Meridian Health
            stage="Applied",
            applied_date="2026-10-18",
            follow_up_date="2026-10-28",
            notes="Submitted full-stack tailored resume highlighting CloudMetrics project. Recruiter confirmed receipt."
        )
        app2 = Application(
            user_id=demo_user.id,
            job_id=saved_jobs_created[1].id,  # Loomis Commerce
            stage="Assessment",
            applied_date="2026-10-14",
            follow_up_date="2026-10-26",
            notes="Take-home design system coding challenge received. Due in 4 days."
        )
        app3 = Application(
            user_id=demo_user.id,
            job_id=saved_jobs_created[3].id,  # Beacon Analytics
            stage="Interview",
            applied_date="2026-10-10",
            interview_date="2026-10-29 14:00 IST",
            notes="Round 2 technical architectural review with engineering lead."
        )
        db.add_all([app1, app2, app3])

        # Also bookmark Meridian Health
        sj = SavedJob(
            user_id=demo_user.id,
            job_id=saved_jobs_created[0].id,
            status="saved",
            notes="High match (93%). Focus on FastAPI and PostgreSQL evidence."
        )
        db.add(sj)

        # 9. Seed 30-Day Adaptive Career Plan
        plan = CareerPlan(
            user_id=demo_user.id,
            target_role="Full Stack Software Engineer",
            target_job_id=saved_jobs_created[0].id,
            duration_days=30,
            current_day=7,
            status="active"
        )
        db.add(plan)
        await db.flush()

        plan_tasks = generate_30_day_plan_tasks(
            target_role="Full Stack Software Engineer",
            skill_gaps=[{"skill": "Docker", "priority": "High"}, {"skill": "Kubernetes", "priority": "Medium"}],
            target_job_title=saved_jobs_created[0].title
        )
        for i, pt in enumerate(plan_tasks):
            # Mark first 3 as completed for demonstration progress
            is_done = i < 3
            task_obj = CareerPlanTask(
                plan_id=plan.id,
                stage=pt["stage"],
                day_number=pt["day_number"],
                title=pt["title"],
                description=pt["description"],
                linked_skill=pt["linked_skill"],
                priority=pt["priority"],
                duration_hours=pt["duration_hours"],
                due_date=pt["due_date"],
                status="completed" if is_done else "pending",
                completion_evidence="Attached CloudMetrics GitHub commits & profile verified links." if is_done else "",
                completed_at=datetime.now(timezone.utc) if is_done else None
            )
            db.add(task_obj)

        # 10. Seed Initial Audit Events
        audit_events = [
            ("profile_edit", {"field": "headline", "value": profile.headline}),
            ("evidence_approved", {"claim": "Python", "source": "CloudMetrics Project"}),
            ("evidence_approved", {"claim": "React", "source": "LoomUI Project"}),
            ("job_submitted", {"job": "Meridian Health", "status": "assessed"}),
            ("application_stage_change", {"application": "Loomis Commerce", "old_stage": "Planned", "new_stage": "Assessment"}),
            ("career_task_updated", {"task": "Profile & Evidence Audit", "status": "completed"})
        ]
        for ev_type, details in audit_events:
            event = AuditEvent(
                user_id=demo_user.id,
                event_type=ev_type,
                details_json=json.dumps(details)
            )
            db.add(event)

        await db.commit()
        print("Initial demonstration data seeded successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_initial_data())
