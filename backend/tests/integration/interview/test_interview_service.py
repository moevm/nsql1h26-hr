import pytest
from uuid import uuid4, UUID
from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models.interview import (
    InterviewPatch,
    InterviewCreate,
    InterviewResult,
    InterviewFilter,
    InterviewSort,
)
from app.models.helpers import SortOrder
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate
from app.services.interview_service import InterviewService
from app.services.candidate_service import CandidateService
from app.repositories.interview_repo import InterviewRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.user_repo import UserRepository
from app.core.exceptions import AppError

from app.models.user import UserCreate, Role
from app.services.user_service import UserService


@pytest.fixture
async def user_service(user_repo):
    return UserService(user_repo)


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
def candidate_service(neo4j_driver):
    return CandidateService(
        TestTaskRepository(neo4j_driver),
        VacancyRepository(neo4j_driver),
        CandidateRepository(neo4j_driver),
    )


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
async def tech_spec_user(user_service):
    user = await user_service.create_user(
        UserCreate(
            email="tech.service@example.com",
            full_name="Tech Service",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    return user.id


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


async def test_get_interview_by_id_ok(
    interview_service, test_candidate, tech_spec_user
):
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


async def test_filter_interviews_ok(
    user_service, interview_service, test_candidate, tech_spec_user, neo4j_driver
):
    tech_spec_2_user = await user_service.create_user(
        UserCreate(
            email="tech2@service.com",
            full_name="Tech Two",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    tech_spec_2 = tech_spec_2_user.id

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
    assert result.total == 1
    assert result.items[0].result == InterviewResult.INTERVIEW_PASSED


async def test_filter_interviews_with_sorting(
    interview_service, test_candidate, tech_spec_user, candidate_repo, test_vacancy
):
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Anna",
            email="anna@ex.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"],
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Zoe",
            email="zoe@ex.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"],
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
        sort_by=InterviewSort.SCHEDULED_AT, sort_order=SortOrder.ASC
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
            vacancy_id=test_vacancy["id"],
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Jane Doe",
            email="jane@example.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"],
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

    filters = InterviewFilter(candidate_name="john")
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert result.items[0].candidate_id == c1_id


async def test_filter_interviews_by_tech_spec_name(
    user_service, interview_service, test_candidate, neo4j_driver
):
    """Фильтр по подстроке в имени технического специалиста."""
    tech_a_user = await user_service.create_user(
        UserCreate(
            email="alpha@example.com",
            full_name="Tech Alpha",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    tech_b_user = await user_service.create_user(
        UserCreate(
            email="beta@example.com",
            full_name="Tech Beta",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    tech_a = tech_a_user.id
    tech_b = tech_b_user.id

    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_a,
            scheduled_at=now + timedelta(days=1),
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_b,
            scheduled_at=now + timedelta(days=2),
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
            feedback="Great candidate, very strong skills",
        )
    )
    # интервью без фидбека
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(days=2),
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
            scheduled_at=t1,
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=t2,
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=t3,
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
    for i in range(3):
        await interview_service.create_interview(
            InterviewCreate(
                candidate_id=test_candidate["id"],
                tech_spec_id=tech_spec_user,
                scheduled_at=now + timedelta(days=i + 1),
            )
        )

    # limit=2, offset=0 должно вернуться 2 элемента, total=3
    filters = InterviewFilter(limit=2, offset=0)
    result = await interview_service.filter_interviews(filters)
    assert result.total == 3
    assert len(result.items) == 2

    # offset=1 всё ещё 3 всего, но два других элемента
    filters.offset = 1
    result = await interview_service.filter_interviews(filters)
    assert result.total == 3
    assert len(result.items) == 2
    # проверка, что первый элемент из второго запроса не совпадает с первым из первого запроса
    first_page_ids = {
        i.id
        for i in (
            await interview_service.filter_interviews(
                InterviewFilter(limit=2, offset=0)
            )
        ).items
    }
    second_page_ids = {i.id for i in result.items}
    # пересечение должно быть минимальным (только один общий, если limit=2 offset=1 при трёх записях)
    assert len(first_page_ids & second_page_ids) == 1


async def test_filter_interviews_sorting_by_result(
    interview_service, test_candidate, tech_spec_user
):
    """Сортировка по result (по возрастанию)."""
    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now,
            result=InterviewResult.INTERVIEW_PASSED,
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(hours=1),
            result=InterviewResult.AWAIT_INTERVIEW,
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(hours=2),
            result=InterviewResult.INTERVIEW_FAILED,
        )
    )

    filters = InterviewFilter(sort_by=InterviewSort.RESULT, sort_order=SortOrder.ASC)
    result = await interview_service.filter_interviews(filters)
    assert result.total == 3
    # Ожидаемый алфавитный порядок enum-значений
    expected_order = [
        InterviewResult.AWAIT_INTERVIEW,
        InterviewResult.INTERVIEW_FAILED,
        InterviewResult.INTERVIEW_PASSED,
    ]
    assert [item.result for item in result.items] == expected_order


async def test_filter_interviews_sorting_by_candidate_name(
    interview_service, candidate_repo, test_vacancy, tech_spec_user
):
    """Сортировка по имени кандидата (по возрастанию)."""
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Zoe",
            email="zoe@example.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"],
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Anna",
            email="anna@example.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"],
        )
    )
    c1_id = UUID(c1["id"])
    c2_id = UUID(c2["id"])
    now = datetime.now(timezone.utc)

    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c1_id, tech_spec_id=tech_spec_user, scheduled_at=now
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c2_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(hours=1),
        )
    )

    filters = InterviewFilter(
        sort_by=InterviewSort.CANDIDATE_NAME, sort_order=SortOrder.ASC
    )
    result = await interview_service.filter_interviews(filters)
    assert result.total == 2
    # Anna должна идти раньше Zoe
    assert result.items[0].candidate_id == c2_id
    assert result.items[1].candidate_id == c1_id


async def test_filter_interviews_sorting_by_tech_spec_name(
    interview_service, test_candidate, user_service
):
    """Сортировка по имени технического специалиста (по возрастанию)."""
    tech_z_user = await user_service.create_user(
        UserCreate(
            email="z@example.com",
            full_name="Zoe Tech",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    tech_a_user = await user_service.create_user(
        UserCreate(
            email="a@example.com",
            full_name="Anna Tech",
            password="hash123456",
            role=Role.TECH_SPEC,
        )
    )
    tech_z = tech_z_user.id
    tech_a = tech_a_user.id

    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"], tech_spec_id=tech_z, scheduled_at=now
        )
    )
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_a,
            scheduled_at=now + timedelta(hours=1),
        )
    )

    filters = InterviewFilter(
        sort_by=InterviewSort.TECH_SPEC_NAME, sort_order=SortOrder.ASC
    )
    result = await interview_service.filter_interviews(filters)
    assert result.total == 2
    assert result.items[0].tech_spec_id == tech_a  # Anna
    assert result.items[1].tech_spec_id == tech_z  # Zoe


async def test_filter_interviews_empty_result(
    interview_service, test_candidate, tech_spec_user
):
    """Фильтр, который не даёт результатов, возвращает total=0 и пустой список."""
    now = datetime.now(timezone.utc)
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=test_candidate["id"],
            tech_spec_id=tech_spec_user,
            scheduled_at=now,
        )
    )

    filters = InterviewFilter(candidate_name="NonExistentName")
    result = await interview_service.filter_interviews(filters)
    assert result.total == 0
    assert result.items == []


async def test_filter_interviews_combined_filters(
    interview_service, candidate_repo, test_vacancy, tech_spec_user
):
    """Комбинация фильтров: result и candidate_name одновременно."""
    c1 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="John Wick",
            email="johnwick@example.com",
            phone="+71234567890",
            status="NEW",
            vacancy_id=test_vacancy["id"],
        )
    )
    c2 = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="John McClane",
            email="mcclane@example.com",
            phone="+71234567891",
            status="NEW",
            vacancy_id=test_vacancy["id"],
        )
    )
    c1_id = UUID(c1["id"])
    c2_id = UUID(c2["id"])
    now = datetime.now(timezone.utc)

    # Первое интервью: John Wick + INTERVIEW_PASSED
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c1_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now,
            result=InterviewResult.INTERVIEW_PASSED,
        )
    )
    # Второе: John McClane + INTERVIEW_FAILED
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c2_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(hours=1),
            result=InterviewResult.INTERVIEW_FAILED,
        )
    )
    # Третье: ещё один John Wick, но с другим результатом
    await interview_service.create_interview(
        InterviewCreate(
            candidate_id=c1_id,
            tech_spec_id=tech_spec_user,
            scheduled_at=now + timedelta(hours=2),
            result=InterviewResult.AWAIT_INTERVIEW,
        )
    )

    filters = InterviewFilter(
        result=InterviewResult.INTERVIEW_PASSED, candidate_name="john"
    )
    result = await interview_service.filter_interviews(filters)
    assert result.total == 1
    assert result.items[0].candidate_id == c1_id
    assert result.items[0].result == InterviewResult.INTERVIEW_PASSED


async def test_patch_interview_to_failed(
    interview_service, test_candidate, tech_spec_user
):
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
    patch = InterviewPatch(
        feedback="Good, Anakin, good", result=InterviewResult.INTERVIEW_FAILED
    )
    patched = await interview_service.patch_interview(created.id, patch)
    assert patched is not None
    assert patched.id is not None
    assert patched.candidate_id == test_candidate["id"]
    assert patched.tech_spec_id == tech_spec_user
    assert patched.scheduled_at == scheduled_at
    assert str(patched.zoom_url) == "https://zoom.us/test"
    assert patched.result == patch.result
    assert patched.feedback == patch.feedback


async def test_patch_interview_to_passed(
    interview_service, candidate_service, test_candidate, tech_spec_user
):
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
    patch = InterviewPatch(
        feedback="Good, Anakin, good", result=InterviewResult.INTERVIEW_PASSED
    )
    patched = await interview_service.patch_interview(created.id, patch)
    candidate = await candidate_service.get_candidate_by_id(interview_data.candidate_id)
    assert patched is not None
    assert patched.id is not None
    assert patched.candidate_id == test_candidate["id"]
    assert patched.tech_spec_id == tech_spec_user
    assert patched.scheduled_at == scheduled_at
    assert str(patched.zoom_url) == "https://zoom.us/test"
    assert patched.result == patch.result
    assert patched.feedback == patch.feedback
    assert candidate.status == CandidateStatus.OFFER
async def test_filter_by_date_range(interview_service):
    result = await interview_service.filter_interviews(
        InterviewFilter(
            scheduled_at_from=1000,
            scheduled_at_to=2000
        )
    )
    assert all(1000 <= i.scheduled_at <= 2000 for i in result.items)
