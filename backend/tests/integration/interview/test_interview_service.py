import pytest
from uuid import uuid4, UUID
from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models.interview import InterviewCreate, InterviewResult, InterviewFilter, InterviewSort
from app.models.helpers import SortOrder
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate
from app.services.interview_service import InterviewService
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.user_repo import UserRepository
from app.core.exceptions import AppError

@pytest.fixture
async def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


@pytest.fixture
async def candidate_repo(neo4j_driver):
    return CandidateRepository(neo4j_driver)


@pytest.fixture
async def user_repo(neo4j_driver):
    return UserRepository(neo4j_driver)


@pytest.fixture
async def interview_repo(neo4j_driver):
    return InterviewRepository(neo4j_driver)


@pytest.fixture
async def interview_service(interview_repo, candidate_repo, user_repo):
    return InterviewService(interview_repo, candidate_repo, user_repo)


@pytest.fixture
async def test_vacancy(vacancy_repo):
    return await vacancy_repo.create_vacancy(
        VacancyCreate(title="Interview Vacancy", description="For service tests")
    )


@pytest.fixture
async def test_candidate(candidate_repo, test_vacancy):
    candidate = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Service Candidate",
            email="service@example.com",
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
            id=str(user_id), email="tech.service@example.com", full_name="Tech Service", hash="hash"
        )
    return user_id


async def test_create_interview_ok(interview_service, test_candidate, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    interview_data = InterviewCreate(
        candidate_id=test_candidate["id"],
        tech_spec_id=tech_spec_user,
        scheduled_at=scheduled_at,
        zoom_url="https://zoom.us/test",
        feedback=None,
        result=InterviewResult.AWAIT_INTERVIEW,
    )
    created = await interview_service.create_interview(interview_data)
    assert created is not None
    assert created.id is not None
    assert created.candidate_id == test_candidate["id"]
    assert created.tech_spec_id == tech_spec_user
    assert created.scheduled_at == scheduled_at
    assert str(created.zoom_url) == "https://zoom.us/test"
    assert created.result == InterviewResult.AWAIT_INTERVIEW


async def test_create_interview_candidate_not_found(interview_service, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    interview_data = InterviewCreate(
        candidate_id=uuid4(),
        tech_spec_id=tech_spec_user,
        scheduled_at=scheduled_at,
    )
    with pytest.raises(AppError) as ex:
        await interview_service.create_interview(interview_data)
        assert ex.value.args[1] == status.HTTP_400_BAD_REQUEST


async def test_create_interview_tech_spec_not_found(interview_service, test_candidate):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    interview_data = InterviewCreate(
        candidate_id=test_candidate["id"],
        tech_spec_id=uuid4(),
        scheduled_at=scheduled_at,
    )
    with pytest.raises(AppError) as ex:
        await interview_service.create_interview(interview_data)
        assert ex.value.args[1] == status.HTTP_400_BAD_REQUEST


async def test_get_interview_by_id_ok(interview_service, test_candidate, tech_spec_user):
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    create_data = InterviewCreate(
        candidate_id=test_candidate["id"],
        tech_spec_id=tech_spec_user,
        scheduled_at=scheduled_at,
        zoom_url="https://zoom.us/unique",
        result=InterviewResult.INTERVIEW_PASSED,
    )
    created = await interview_service.create_interview(create_data)
    assert created is not None

    fetched = await interview_service.get_interview_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.candidate_id == test_candidate["id"]
    assert fetched.tech_spec_id == tech_spec_user
    assert str(fetched.zoom_url) == "https://zoom.us/unique"
    assert fetched.result == InterviewResult.INTERVIEW_PASSED


async def test_get_interview_by_id_not_found(interview_service):
    with pytest.raises(AppError) as ex:
        await interview_service.get_interview_by_id(uuid4())
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND


async def test_filter_interviews_ok(interview_service, test_candidate, tech_spec_user, neo4j_driver):
    tech_spec_2 = uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_spec_2), email="tech2@service.com", full_name="Tech Two", hash="hash"
        )

    now = datetime.now(timezone.utc)
    interview1 = await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=1),
            result=InterviewResult.INTERVIEW_PASSED,
        )
    )
    interview2 = await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_2,
            scheduled_at=now + timedelta(days=2),
            result=InterviewResult.INTERVIEW_FAILED,
        )
    )
    assert interview1 is not None
    assert interview2 is not None

    filters = InterviewFilter()
    result = await interview_service.filter_interviews(filters)
    assert result.total == 2
    returned_ids = {item.id for item in result.items}
    assert {interview1.id, interview2.id} == returned_ids

    filters = InterviewFilter(result=InterviewResult.INTERVIEW_PASSED)
    result = await interview_service.filter_interviews(filters)
    # Следующая строка упадёт с ValidationError из-за бага в репозитории
    assert result.total == 1
    assert result.items[0].result == InterviewResult.INTERVIEW_PASSED


async def test_filter_interviews_with_sorting(interview_service, test_candidate, tech_spec_user, candidate_repo, test_vacancy):
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Anna",
            email="anna@ex.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"]
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Zoe",
            email="zoe@ex.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"]
        )
    )
    c1_id = UUID(c1["id"])
    c2_id = UUID(c2["id"])
    now = datetime.now(timezone.utc)

    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c1_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=1),
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c2_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=2),
        )
    )

    filters = InterviewFilter(
        sort_by=InterviewSort.SCHEDULED_AT,
        sort_order=SortOrder.ASC
    )
    result = await interview_service.filter_interviews(filters)
    assert result.total == 2
    assert result.items[0].scheduled_at < result.items[1].scheduled_at
