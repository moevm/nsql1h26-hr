import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from app.models.interview import InterviewCreate, InterviewResult, InterviewFilter, InterviewSort
from app.models.helpers import SortOrder
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate


@pytest.fixture
async def interview_repo(neo4j_driver):
    return InterviewRepository(neo4j_driver)


@pytest.fixture
async def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


@pytest.fixture
async def candidate_repo(neo4j_driver):
    return CandidateRepository(neo4j_driver)


@pytest.fixture
async def test_vacancy(vacancy_repo):
    return await vacancy_repo.create_vacancy(
        VacancyCreate(title="Vacancy for Interview", description="Desc")
    )


@pytest.fixture
async def test_candidate(candidate_repo, test_vacancy):
    candidate = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="John Doe",
            email="john@example.com",
            phone="+71234567890",
            status=CandidateStatus.NEW,
            vacancy_id=test_vacancy["id"],
        )
    )
    candidate["id"] = UUID(candidate["id"])
    return candidate


@pytest.fixture
async def tech_spec_user(neo4j_driver):
    user_id = uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(user_id), email="tech@spec.com", full_name="Tech Spec", hash="hash"
        )
    return user_id


async def test_get_interview_by_id(interview_repo, test_candidate, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    create_data = InterviewCreate(
        candidate_id=test_candidate["id"],
        tech_spec_id=tech_spec_user,
        scheduled_at=scheduled_at,
        zoom_url="https://zoom.us/123",
        feedback=None,
        result=InterviewResult.INTERVIEW_FAILED,
    )
    created = await interview_repo.create_interview(create_data)
    assert created is not None

    fetched = await interview_repo.get_interview_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.candidate_id == test_candidate["id"]
    assert fetched.tech_spec_id == tech_spec_user


async def test_get_interview_by_id_not_found(interview_repo):
    fetched = await interview_repo.get_interview_by_id(uuid4())
    assert fetched is None