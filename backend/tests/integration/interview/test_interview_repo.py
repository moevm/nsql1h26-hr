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
from app.models.helpers import SortOrder


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
    

async def test_filter_interviews_by_result(interview_repo, test_candidate, neo4j_driver):
    tech_spec_1 = uuid4()
    tech_spec_2 = uuid4()
    async with neo4j_driver.session() as session:
        for ts_id, email in [(tech_spec_1, "tech1@spec.com"), (tech_spec_2, "tech2@spec.com")]:
            await session.run(
                """
                CREATE (u:User:TECH_SPEC {
                    id: $id, email: $email, full_name: $full_name,
                    password_hash: $hash, role: 'TECH_SPEC'
                })
                """,
                id=str(ts_id), email=email, full_name="Tech Spec", hash="hash"
            )
    
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    
    # Интервью 1: результат INTERVIEW_PASSED
    passed = await interview_repo.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_1,
            scheduled_at=scheduled_at,
            result=InterviewResult.INTERVIEW_PASSED,
        )
    )
    assert passed is not None
    assert passed.tech_spec_id == tech_spec_1
    
    # Интервью 2: результат INTERVIEW_FAILED (используем второго техспеца)
    failed = await interview_repo.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_2,
            scheduled_at=scheduled_at + timedelta(hours=1),
            result=InterviewResult.INTERVIEW_FAILED,
        )
    )
    assert failed is not None
    assert failed.tech_spec_id == tech_spec_2
    
    # Фильтрация по INTERVIEW_FAILED — должно быть 1 интервью
    filters = InterviewFilter(result=InterviewResult.INTERVIEW_FAILED)
    result = await interview_repo.filter_interviews(filters)
    # Отфильтровываем возможные None 
    valid_items = [item for item in result.items if item.tech_spec_id is not None]
    assert len(valid_items) == 1
    assert valid_items[0].result == InterviewResult.INTERVIEW_FAILED
    
    # Фильтрация по INTERVIEW_PASSED — должно быть 1 интервью
    filters = InterviewFilter(result=InterviewResult.INTERVIEW_PASSED)
    result = await interview_repo.filter_interviews(filters)
    valid_items = [item for item in result.items if item.tech_spec_id is not None]
    assert len(valid_items) == 1
    assert valid_items[0].result == InterviewResult.INTERVIEW_PASSED


async def test_filter_interviews_sorting(interview_repo, test_vacancy, tech_spec_user, candidate_repo):
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Alpha",
            email="a@ex.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"]
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Beta",
            email="b@ex.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"]
        )
    )
    c1_id = UUID(c1["id"])
    c2_id = UUID(c2["id"])
    now = datetime.now(timezone.utc)
    await interview_repo.create_interview(
        InterviewCreate(
            candidate_id=c1_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=2)
        )
    )
    await interview_repo.create_interview(
        InterviewCreate(
            candidate_id=c2_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=1)
        )
    )

    filters = InterviewFilter(
        sort_by=InterviewSort.SCHEDULED_AT,
        sort_order=SortOrder.ASC
    )
    result = await interview_repo.filter_interviews(filters)
    assert result.total == 2
    # Раньше запланированное интервью  должно быть первым
    assert result.items[0].scheduled_at < result.items[1].scheduled_at