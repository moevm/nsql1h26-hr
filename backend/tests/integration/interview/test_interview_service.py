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


async def test_filter_interviews_by_candidate_name(
    interview_service, candidate_repo, test_vacancy, tech_spec_user
):
    """Фильтр по подстроке в имени кандидата."""
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="John Smith",
            email="john@example.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"]
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Jane Doe",
            email="jane@example.com",
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
            scheduled_at=now + timedelta(days=1)
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c2_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=2)
        )
    )

    filters = InterviewFilter(candidate_name="john")
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert result.items[0].candidate_id == c1_id


async def test_filter_interviews_by_tech_spec_name(
    interview_service, test_candidate, neo4j_driver
):
    """Фильтр по подстроке в имени технического специалиста."""
    tech_a = uuid4()
    tech_b = uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_a), email="alpha@example.com", full_name="Tech Alpha", hash="hash"
        )
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_b), email="beta@example.com", full_name="Tech Beta", hash="hash"
        )

    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_a,
            scheduled_at=now + timedelta(days=1)
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_b,
            scheduled_at=now + timedelta(days=2)
        )
    )

    filters = InterviewFilter(tech_spec_name="alpha")
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert result.items[0].tech_spec_id == tech_a


async def test_filter_interviews_by_feedback_contains(
    interview_service, test_candidate, tech_spec_user
):
    """Фильтр по содержимому фидбека."""
    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=1),
            feedback="Great candidate, very strong skills"
        )
    )
    # интервью без фидбека
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=2)
        )
    )

    filters = InterviewFilter(feedback_contains="very strong")
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert "very strong" in result.items[0].feedback.lower()


async def test_filter_interviews_by_scheduled_at_range(
    interview_service, test_candidate, tech_spec_user
):
    """Фильтр по диапазону дат через Unix timestamp (scheduled_at_from / scheduled_at_to)."""
    now = datetime.now(timezone.utc)
    t1 = now + timedelta(days=1)
    t2 = now + timedelta(days=2)
    t3 = now + timedelta(days=3)

    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=t1
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=t2
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=t3
        )
    )

    # Диапазон от (t1 + 12 часов) до (t3 - 12 часов) должен захватить только t2
    from_ts = int((t1 + timedelta(hours=12)).timestamp())
    to_ts = int((t3 - timedelta(hours=12)).timestamp())

    filters = InterviewFilter(scheduled_at_from=from_ts, scheduled_at_to=to_ts)
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert result.items[0].scheduled_at == t2


async def test_filter_interviews_pagination(
    interview_service, test_candidate, tech_spec_user
):
    """Пагинация через limit и offset."""
    now = datetime.now(timezone.utc)
    # Создаём 3 интервью для одного кандидата
    for i in range(3):
        await interview_service.create_interview(
            InterviewCreate(
                candidate_id=test_candidate["id"],
                tech_spec_id=tech_spec_user,
                scheduled_at=now + timedelta(days=i + 1)
            )
        )

    # limit=2, offset=0 -> должно вернуться 2 элемента, total=3
    filters = InterviewFilter(limit=2, offset=0)
    result = await interview_service.filter_interviews(filters)
    assert result.total == 3
    assert len(result.items) == 2

    # offset=1 -> всё ещё 3 всего, но два других элемента
    filters.offset = 1
    result = await interview_service.filter_interviews(filters)
    assert result.total == 3
    assert len(result.items) == 2
    # убедимся, что первый элемент из второго запроса не совпадает с первым из первого запроса
    first_page_ids = {i.id for i in (await interview_service.filter_interviews(InterviewFilter(limit=2, offset=0))).items}
    second_page_ids = {i.id for i in result.items}
    # пересечение должно быть минимальным (только один общий, если limit=2 offset=1 при трёх записях)
    assert len(first_page_ids & second_page_ids) == 1

