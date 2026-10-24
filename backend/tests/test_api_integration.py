import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import engine, Base
from backend.app.seed_data import seed_initial_data

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield

@pytest.mark.asyncio
async def test_api_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_auth_login_and_me():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login with seed user Alex Morgan
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "alex.morgan@careerloom.dev",
            "password": "password123"
        })
        assert login_res.status_code == 200
        data = login_res.json()
        token = data["access_token"]
        assert token is not None

        # Verify /me endpoint
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "alex.morgan@careerloom.dev"

@pytest.mark.asyncio
async def test_unauthorized_access_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/auth/me")
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_dashboard_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "alex.morgan@careerloom.dev",
            "password": "password123"
        })
        token = login_res.json()["access_token"]

        dash_res = await client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
        assert dash_res.status_code == 200
        d_data = dash_res.json()
        assert d_data["stats"]["profile_completeness"] > 0
        assert "recommended_opportunities" in d_data
        assert len(d_data["recommended_opportunities"]) > 0

@pytest.mark.asyncio
async def test_job_listing_and_scam_assessment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Evaluate scam listing
        eval_res = await client.post("/api/v1/assessments/evaluate", json={
            "title": "Online Typing Clerk",
            "employer": "QuickCash Hub",
            "description": "Earn $200/hr from home! Send $60 security deposit wire before materials can be delivered.",
            "contact_email": "quickcash@gmail.com"
        })
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert eval_data["risk_tier"] == "Elevated risk indicators"
        assert len(eval_data["signals"]) > 0

@pytest.mark.asyncio
async def test_scam_benchmark_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bench_res = await client.get("/api/v1/assessments/benchmark")
        assert bench_res.status_code == 200
        bench_data = bench_res.json()
        assert bench_data["dataset_size"] >= 40
        assert bench_data["metrics"]["accuracy"] > 85.0

@pytest.mark.asyncio
async def test_fairness_audit_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        f_res = await client.get("/api/v1/fairness/audit")
        assert f_res.status_code == 200
        f_data = f_res.json()
        assert f_data["rank_shifts_detected"] == 0

@pytest.mark.asyncio
async def test_career_plan_and_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "alex.morgan@careerloom.dev",
            "password": "password123"
        })
        token = login_res.json()["access_token"]

        plan_res = await client.get("/api/v1/career-plans/current", headers={"Authorization": f"Bearer {token}"})
        assert plan_res.status_code == 200
        p_data = plan_res.json()
        assert p_data["plan"] is not None
        assert len(p_data["tasks"]) == 16

        # Complete a task
        first_task = p_data["tasks"][3]
        upd_res = await client.put(f"/api/v1/career-plans/tasks/{first_task['id']}", json={
            "status": "completed",
            "completion_evidence": "Automated test verification evidence"
        }, headers={"Authorization": f"Bearer {token}"})
        assert upd_res.status_code == 200

@pytest.mark.asyncio
async def test_interview_session_and_practice():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "alex.morgan@careerloom.dev",
            "password": "password123"
        })
        token = login_res.json()["access_token"]

        sess_res = await client.post("/api/v1/interviews/sessions", json={
            "role_title": "Full Stack Software Engineer",
            "interview_type": "Technical"
        }, headers={"Authorization": f"Bearer {token}"})
        assert sess_res.status_code == 200
        sess_data = sess_res.json()
        assert len(sess_data["questions"]) > 0

        q_id = sess_data["questions"][0]["id"]
        prac_res = await client.post("/api/v1/interviews/practice", json={
            "question_id": q_id,
            "user_response": "In our project, we implemented async connection pools with SQLAlchemy to prevent event loop blocking. This reduced P99 latency by 40%."
        }, headers={"Authorization": f"Bearer {token}"})
        assert prac_res.status_code == 200
        prac_data = prac_res.json()
        assert prac_data["feedback_score"] >= 75.0
