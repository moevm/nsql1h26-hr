import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from app.models.interview import InterviewCreate, InterviewFilter, InterviewResult, InterviewSort
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.user_repo import UserRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.user import Role
from app.models.vacancy import VacancyCreate

@pytest.fixture
async def interview_repo(neo4j_driver):
    return InterviewRepository(neo4j_driver)

@pytest.fixture
async def candidate(neo4j_driver):
    vacancy_repo = VacancyRepository(neo4j_driver)
    vacancy = await vacancy_repo.create_vacancy(VacancyCreate(title="Test", description="Desc"))
    candidate_repo = CandidateRepository(neo4j_driver)
    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john@example.com",
        phone="+71234567890",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy["id"],
        test_task_id=None,
    )
    return await candidate_repo.create_candidate(candidate_data)

@pytest.fixture
async def tech_spec_user(neo4j_driver):
    user_repo = UserRepository(neo4j_driver)
    user_data = {
        "email": "tech@example.com",
        "full_name": "Tech Spec",
        "password_hash": "hash",
        "role": Role.TECH_SPEC,
    }
    return await user_repo.create_user(user_data)

async def test_create_interview(interview_repo, candidate, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    interview_data = InterviewCreate(
        candidate_id=candidate["id"],
        tech_spec_id=tech_spec_user.id,
        scheduled_at=scheduled_at,
        zoom_url="https://zoom.us/123",
        feedback=None,
        result=InterviewResult.AWAIT_INTERVIEW,
    )
    result = await interview_repo.create_interview(interview_data)

    assert result.id is not None
    assert result.candidate_id == candidate["id"]
    assert result.tech_spec_id == tech_spec_user.id
    assert result.scheduled_at == scheduled_at
    assert result.zoom_url == "https://zoom.us/123"
    assert result.feedback is None
    assert result.result == InterviewResult.AWAIT_INTERVIEW

    # Смена статуса кандидата на INTERVIEW
    candidate_repo = CandidateRepository(interview_repo.driver)
    updated_candidate = await candidate_repo.get_candidate_by_id(candidate["id"])
    assert updated_candidate["status"] == "INTERVIEW"

async def test_create_interview_candidate_not_found(interview_repo, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    interview_data = InterviewCreate(
        candidate_id=uuid4(),
        tech_spec_id=tech_spec_user.id,
        scheduled_at=scheduled_at,
    )
    result = await interview_repo.create_interview(interview_data)
    assert result is None
