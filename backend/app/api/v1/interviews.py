import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile, CandidateSkill, Project
from backend.app.models.job import JobListing
from backend.app.models.interview import InterviewSession, InterviewQuestion, InterviewPractice
from backend.app.api.deps import get_current_user
from backend.app.services.interview_service import generate_interview_questions, evaluate_candidate_answer
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/interviews", tags=["Interview Studio"])

class CreateSessionRequest(BaseModel):
    role_title: str
    job_id: Optional[str] = None
    interview_type: Optional[str] = "Technical"
    difficulty: Optional[str] = "Intermediate"

class SubmitPracticeRequest(BaseModel):
    question_id: str
    user_response: str

@router.post("/sessions")
async def create_interview_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()

    cand_skills = []
    cand_projects = []
    if profile:
        s_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
        cand_skills = [s.canonical_name for s in s_res.scalars().all()]
        p_res = await db.execute(select(Project).where(Project.profile_id == profile.id))
        cand_projects = [{"title": p.title, "description": p.description} for p in p_res.scalars().all()]

    session = InterviewSession(
        user_id=current_user.id,
        job_id=req.job_id,
        role_title=req.role_title,
        interview_type=req.interview_type or "Technical",
        difficulty=req.difficulty or "Intermediate"
    )
    db.add(session)
    await db.flush()

    # Generate questions grounded in role & projects
    questions_data = generate_interview_questions(
        role_title=req.role_title,
        candidate_skills=cand_skills,
        candidate_projects=cand_projects,
        interview_type=req.interview_type or "Technical"
    )

    created_questions = []
    for qd in questions_data:
        q_obj = InterviewQuestion(
            session_id=session.id,
            question_type=qd["question_type"],
            question_text=qd["question_text"],
            context_rationale=qd.get("context_rationale", ""),
            suggested_framework=qd.get("suggested_framework", ""),
            linked_skill=qd.get("linked_skill", ""),
            linked_project=qd.get("linked_project", "")
        )
        db.add(q_obj)
        created_questions.append(q_obj)

    await db.commit()
    await db.refresh(session)

    await log_audit_event(db, current_user.id, "interview_session_created", {
        "session_id": session.id,
        "role_title": session.role_title,
        "question_count": len(created_questions)
    })

    return {
        "id": session.id,
        "role_title": session.role_title,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "questions": [
            {
                "id": q.id,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "context_rationale": q.context_rationale,
                "suggested_framework": q.suggested_framework,
                "linked_skill": q.linked_skill,
                "linked_project": q.linked_project
            } for q in created_questions
        ]
    }

@router.get("/sessions/{session_id}")
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    s_res = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id))
    session = s_res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    q_res = await db.execute(select(InterviewQuestion).where(InterviewQuestion.session_id == session.id))
    questions = q_res.scalars().all()

    # Load practice responses
    formatted_questions = []
    for q in questions:
        p_res = await db.execute(
            select(InterviewPractice).where(InterviewPractice.question_id == q.id, InterviewPractice.user_id == current_user.id).order_by(InterviewPractice.practiced_at.desc())
        )
        latest_practice = p_res.scalar_one_or_none()
        
        practice_data = None
        if latest_practice:
            try:
                strengths = json.loads(latest_practice.strengths) if latest_practice.strengths else []
                improvements = json.loads(latest_practice.improvements) if latest_practice.improvements else []
            except Exception:
                strengths = []
                improvements = []
            practice_data = {
                "id": latest_practice.id,
                "user_response": latest_practice.user_response,
                "feedback_score": latest_practice.feedback_score,
                "feedback_summary": latest_practice.feedback_summary,
                "strengths": strengths,
                "improvements": improvements,
                "practiced_at": latest_practice.practiced_at.isoformat() if latest_practice.practiced_at else None
            }

        formatted_questions.append({
            "id": q.id,
            "question_type": q.question_type,
            "question_text": q.question_text,
            "context_rationale": q.context_rationale,
            "suggested_framework": q.suggested_framework,
            "linked_skill": q.linked_skill,
            "linked_project": q.linked_project,
            "latest_practice": practice_data
        })

    return {
        "id": session.id,
        "role_title": session.role_title,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "questions": formatted_questions
    }

@router.post("/practice")
async def submit_interview_practice(
    req: SubmitPracticeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    q_res = await db.execute(select(InterviewQuestion).where(InterviewQuestion.id == req.question_id))
    question = q_res.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Interview question not found")

    # Evaluate answer with rubric
    evaluation = evaluate_candidate_answer(
        question_type=question.question_type,
        question_text=question.question_text,
        user_response=req.user_response
    )

    practice = InterviewPractice(
        question_id=question.id,
        user_id=current_user.id,
        user_response=req.user_response,
        feedback_score=evaluation["feedback_score"],
        feedback_summary=evaluation["feedback_summary"],
        strengths=json.dumps(evaluation["strengths"]),
        improvements=json.dumps(evaluation["improvements"])
    )
    db.add(practice)
    await db.commit()
    await db.refresh(practice)

    await log_audit_event(db, current_user.id, "interview_practice_saved", {
        "question_id": question.id,
        "score": evaluation["feedback_score"]
    })

    return {
        "id": practice.id,
        "feedback_score": evaluation["feedback_score"],
        "feedback_summary": evaluation["feedback_summary"],
        "strengths": evaluation["strengths"],
        "improvements": evaluation["improvements"]
    }
