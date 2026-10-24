import re
from typing import List, Dict, Any

DEFAULT_QUESTIONS_BY_ROLE: Dict[str, List[Dict[str, Any]]] = {
    "software_engineer": [
        {
            "question_type": "technical",
            "question_text": "Explain how you design an asynchronous REST API endpoint in Python/FastAPI or Node.js to handle high concurrency while preventing database connection starvation.",
            "context_rationale": "Evaluates architectural awareness of async event loops, connection pooling, and non-blocking I/O.",
            "suggested_framework": "1. Explain event loop non-blocking model; 2. Discuss async connection pool limits (e.g. SQLAlchemy pool_size, max_overflow); 3. Background tasks or message queues (Celery/Redis) for slow work.",
            "linked_skill": "FastAPI"
        },
        {
            "question_type": "project_grounded",
            "question_text": "In your projects, describe a challenging bug or performance bottleneck you encountered. How did you diagnose it, what tools did you use, and what was the quantifiable outcome?",
            "context_rationale": "Assesses authentic troubleshooting competence and empirical debugging evidence.",
            "suggested_framework": "STAR Method: State the specific symptom, profiling tools used (cProfile, Chrome DevTools, EXPLAIN ANALYZE), fix implemented, and performance metric before vs after.",
            "linked_skill": "Debugging & Performance"
        },
        {
            "question_type": "behavioral",
            "question_text": "Tell me about a time when you received critical code review feedback or had a technical disagreement with a team member. How did you handle it?",
            "context_rationale": "Tests emotional intelligence, constructive communication, and collaborative mindset.",
            "suggested_framework": "STAR Method: Situation, Task, Action (listened actively, evaluated objectively, proposed benchmark test), and Result (reached consensus, maintained psychological safety).",
            "linked_skill": "Team Collaboration"
        },
        {
            "question_type": "system_design",
            "question_text": "How would you design a rate limiter for an external public API to prevent denial-of-service abuse while allowing legitimate burst traffic?",
            "context_rationale": "Evaluates knowledge of distributed systems, Token Bucket / Leaky Bucket algorithms, and Redis counters.",
            "suggested_framework": "1. Clarify traffic requirements; 2. Compare algorithms (Token Bucket vs Sliding Window Log); 3. Redis atomic INCR with TTL; 4. HTTP 429 status code and Retry-After headers.",
            "linked_skill": "System Design"
        }
    ],
    "data_engineer": [
        {
            "question_type": "technical",
            "question_text": "How do you ensure idempotency and data consistency in an automated ETL batch processing pipeline that experiences intermittent network failures?",
            "context_rationale": "Evaluates fault tolerance, atomic transactions, and deduplication logic.",
            "suggested_framework": "Discuss atomic upserts (MERGE / ON CONFLICT DO UPDATE), staging tables, cryptographic row hashing, and Airflow retry policies.",
            "linked_skill": "SQL"
        },
        {
            "question_type": "project_grounded",
            "question_text": "Walk me through how you structured data models and queries in your latest database project. What indexes did you create and why?",
            "context_rationale": "Verifies practical database indexing and query optimization experience.",
            "suggested_framework": "Mention B-Tree vs Hash index trade-offs, composite index column order, and analyzing query plans with EXPLAIN.",
            "linked_skill": "PostgreSQL"
        }
    ]
}

def generate_interview_questions(
    role_title: str,
    candidate_skills: List[str],
    candidate_projects: List[Dict[str, Any]],
    interview_type: str = "Technical"
) -> List[Dict[str, Any]]:
    clean_role = role_title.lower()
    base_category = "data_engineer" if "data" in clean_role or "analytics" in clean_role else "software_engineer"
    questions = list(DEFAULT_QUESTIONS_BY_ROLE.get(base_category, DEFAULT_QUESTIONS_BY_ROLE["software_engineer"]))
    
    # If candidate has projects, add project-specific question
    if candidate_projects:
        first_proj = candidate_projects[0]
        p_title = first_proj.get("title", "Recent Project")
        questions.append({
            "question_type": "project_grounded",
            "question_text": f"In your project '{p_title}', what architectural trade-offs did you make when choosing your technology stack, and what would you do differently today?",
            "context_rationale": f"Grounded directly in candidate's project evidence ({p_title}).",
            "suggested_framework": "Discuss architectural constraints, alternative libraries considered, performance benchmarks, and key learnings.",
            "linked_skill": "Architecture & Decision Making",
            "linked_project": p_title
        })

    return questions

def evaluate_candidate_answer(
    question_type: str,
    question_text: str,
    user_response: str
) -> Dict[str, Any]:
    text = user_response.strip()
    word_count = len(text.split())
    
    strengths = []
    improvements = []
    score = 70.0  # Baseline
    
    if word_count < 20:
        score = 40.0
        improvements.append("Response is very brief. Provide concrete implementation details, technical mechanisms, and context.")
        summary = "Answer requires more depth and specific examples to demonstrate competency."
    else:
        # Check for STAR framework in behavioral/project questions
        if question_type in ["behavioral", "project_grounded"]:
            has_situation = bool(re.search(r'(when|situation|context|project|working\s+on)', text, re.IGNORECASE))
            has_action = bool(re.search(r'(i\s+did|i\s+built|i\s+implemented|i\s+created|my\s+role|action)', text, re.IGNORECASE))
            has_result = bool(re.search(r'(result|outcome|improved|reduced|percent|%|delivered|success)', text, re.IGNORECASE))
            
            if has_situation and has_action and has_result:
                score += 20.0
                strengths.append("Structured response effectively following the STAR methodology (Situation, Action, Measurable Result).")
            elif has_action:
                score += 10.0
                strengths.append("Clearly highlighted personal actions and technical implementation.")
                if not has_result:
                    improvements.append("Include quantifiable outcomes or metrics (e.g. latency reduced by 30%, 100% uptime) to substantiate impact.")
            else:
                improvements.append("Use the STAR framework: clearly delineate the Situation, your specific Action, and the final Result.")
                
        # Check for technical depth in technical/system design questions
        if question_type in ["technical", "system_design"]:
            has_tradeoff = bool(re.search(r'(trade-off|tradeoff|however|alternative|limit|bottleneck|versus|vs)', text, re.IGNORECASE))
            has_tooling = bool(re.search(r'(cache|index|async|pool|queue|redis|docker|database|benchmark|scale)', text, re.IGNORECASE))
            
            if has_tradeoff:
                score += 15.0
                strengths.append("Demonstrated senior-level engineering maturity by addressing architectural trade-offs and edge cases.")
            if has_tooling:
                score += 10.0
                strengths.append("Accurately identified appropriate systems, protocols, and tooling components.")
            if not has_tradeoff:
                improvements.append("Discuss alternative approaches and why you selected this particular mechanism over others.")

        if word_count > 80:
            score += 5.0
            strengths.append("Thorough and well-articulated explanation with good narrative continuity.")

        score = min(98.0, max(45.0, score))
        summary = f"Solid answer ({score:.0f}/100). " + ("Shows strong technical grounding." if score >= 80 else "Good foundation with opportunities for added precision.")

    return {
        "feedback_score": round(score, 1),
        "feedback_summary": summary,
        "strengths": strengths or ["Attempted the question directly."],
        "improvements": improvements or ["Continue practicing to maintain fluid verbal delivery under time pressure."]
    }
