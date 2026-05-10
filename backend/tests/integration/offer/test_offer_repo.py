import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from app.models.offer import OfferCreate, OfferStatus, OfferFilter, OfferPatch
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate
from app.models.user import UserCreate, Role


@pytest.fixture
async def test_user(user_repo):
    user = await user_repo.create_user(
        {
            "email": f"hr_{uuid4()}@example.com",
            "full_name": "Test HR",
            "password_hash": "hash",
            "role": Role.HR.value,
        }
    )
    return user


@pytest.fixture
async def test_vacancy(vacancy_repo):
    return await vacancy_repo.create_vacancy(
        VacancyCreate(title="Test Offer Vacancy", description="For offer tests")
    )


@pytest.fixture
async def test_candidate(candidate_repo, test_vacancy):
    """Создаём кандидата в статусе INTERVIEW_PASSED"""
    candidate = await candidate_repo.create_candidate(
        CandidateCreate(
            full_name="Offer Candidate",
            email="offer_candidate@example.com",
            phone="+71234567890",
            status=CandidateStatus.INTERVIEW_PASSED,
            vacancy_id=test_vacancy["id"],
        )
    )
    candidate["id"] = UUID(candidate["id"])
    return candidate


@pytest.fixture
async def test_offer_create_data(test_user, test_candidate, test_vacancy):
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    return OfferCreate(
        candidate_id=test_candidate["id"],
        vacancy_id=UUID(test_vacancy["id"]),
        created_by=test_user.id,
        salary=100000,
        start_at=start_at,
        status=OfferStatus.PENDING,
    )


async def test_create_offer_ok(offer_repo, test_offer_create_data):
    offer = await offer_repo.create_offer(test_offer_create_data)
    assert offer is not None
    assert offer.id is not None


async def test_patch_offer(offer_repo, test_offer_create_data):
    created_offer = await offer_repo.create_offer(test_offer_create_data)
    patched_offer = await offer_repo.patch_offer(
        created_offer.id, OfferPatch(status=OfferStatus.APPROVED_MNG)
    )
    assert patched_offer.status == OfferStatus.APPROVED_MNG
    assert patched_offer.id == created_offer.id


async def test_get_offer_by_id_ok(offer_repo, test_offer_create_data):
    created = await offer_repo.create_offer(test_offer_create_data)
    fetched = await offer_repo.get_offer_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_offer_by_id_not_found(offer_repo):
    assert await offer_repo.get_offer_by_id(uuid4()) is None


async def test_filter_offers_empty(offer_repo):
    """Пустой результат, когда нет данных (фильтр по несуществующему полю)"""
    filters = OfferFilter(candidate_id=uuid4())
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0
    assert result.items == []


async def test_filter_offers_by_salary_range(offer_repo, test_offer_create_data):
    """Фильтр по диапазону зарплаты (salary_from / salary_to)"""
    # Создаём оффер с зарплатой 100000
    await offer_repo.create_offer(test_offer_create_data)

    # Диапазон, включающий эту зарплату
    filters = OfferFilter(salary_from=50000, salary_to=150000)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1

    # Диапазон, не включающий
    filters = OfferFilter(salary_from=150000, salary_to=200000)
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_status(offer_repo, test_offer_create_data):
    """Фильтр по статусу оффера"""
    # Создаём оффер со статусом APPROVED_MNG
    data = test_offer_create_data.model_copy(deep=True)
    data.status = OfferStatus.APPROVED_MNG
    created = await offer_repo.create_offer(data)

    filters = OfferFilter(status=OfferStatus.APPROVED_MNG)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert result.items[0].id == created.id

    # Проверяем, что другие статусы не попадают
    filters = OfferFilter(status=OfferStatus.PENDING)
    result = await offer_repo.filter_offers(filters)
    assert created.id not in [o.id for o in result.items]


async def test_filter_offers_by_candidate_id(offer_repo, test_offer_create_data):
    """Фильтр по ID кандидата"""
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(candidate_id=created.candidate_id)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert all(o.candidate_id == created.candidate_id for o in result.items)

    # Несуществующий кандидат
    filters = OfferFilter(candidate_id=uuid4())
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_vacancy_id(offer_repo, test_offer_create_data):
    """Фильтр по ID вакансии"""
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(vacancy_id=created.vacancy_id)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert all(o.vacancy_id == created.vacancy_id for o in result.items)

    # Несуществующая вакансия
    filters = OfferFilter(vacancy_id=uuid4())
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_pagination(offer_repo, test_offer_create_data):
    """Пагинация (limit / offset)"""
    base = test_offer_create_data
    # Создаём 3 оффера с разными зарплатами для сортировки
    for i in range(3):
        data = OfferCreate(
            candidate_id=base.candidate_id,
            vacancy_id=base.vacancy_id,
            created_by=base.created_by,
            salary=100000 + i * 10000,
            start_at=base.start_at,
        )
        await offer_repo.create_offer(data)

    # Первая страница: limit=2, offset=0
    filters = OfferFilter(limit=2, offset=0, sort_by="salary", sort_order="asc")
    result = await offer_repo.filter_offers(filters)
    assert len(result.items) == 2
    assert result.total == 3

    # Вторая страница: offset=1
    filters.offset = 1
    result_page2 = await offer_repo.filter_offers(filters)
    assert len(result_page2.items) == 2
    # Убедимся, что элементы разные
    first_ids = {o.id for o in result.items}
    second_ids = {o.id for o in result_page2.items}
    assert len(first_ids & second_ids) == 1  # перекрытие (из-за offset=1 при total=3)


async def test_filter_offers_sorting_by_salary(offer_repo, test_offer_create_data):
    """Сортировка по зарплате (ASC / DESC)"""
    base = test_offer_create_data
    salaries = [50000, 150000, 100000]
    created_ids = []
    for sal in salaries:
        data = OfferCreate(
            candidate_id=base.candidate_id,
            vacancy_id=base.vacancy_id,
            created_by=base.created_by,
            salary=sal,
            start_at=base.start_at,
        )
        offer = await offer_repo.create_offer(data)
        created_ids.append(offer.id)

    # ASC
    filters = OfferFilter(sort_by="salary", sort_order="asc")
    result = await offer_repo.filter_offers(filters)
    # Извлекаем зарплаты в порядке сортировки
    salaries_asc = [o.salary for o in result.items if o.id in created_ids]
    assert salaries_asc == sorted(salaries)

    # DESC
    filters.sort_order = "desc"
    result = await offer_repo.filter_offers(filters)
    salaries_desc = [o.salary for o in result.items if o.id in created_ids]
    assert salaries_desc == sorted(salaries, reverse=True)


async def test_filter_offers_sorting_by_start_at(offer_repo, test_offer_create_data):
    """Сортировка по дате начала (start_at)"""
    base = test_offer_create_data
    now = datetime.now(timezone.utc)
    start_dates = [
        now + timedelta(days=10),
        now + timedelta(days=30),
        now + timedelta(days=20),
    ]
    created_ids = []
    for start in start_dates:
        data = OfferCreate(
            candidate_id=base.candidate_id,
            vacancy_id=base.vacancy_id,
            created_by=base.created_by,
            salary=base.salary,
            start_at=start,
        )
        offer = await offer_repo.create_offer(data)
        created_ids.append(offer.id)

    # ASC
    filters = OfferFilter(sort_by="start_at", sort_order="asc")
    result = await offer_repo.filter_offers(filters)
    start_asc = [o.start_at for o in result.items if o.id in created_ids]
    assert start_asc == sorted(start_dates)

    # DESC
    filters.sort_order = "desc"
    result = await offer_repo.filter_offers(filters)
    start_desc = [o.start_at for o in result.items if o.id in created_ids]
    assert start_desc == sorted(start_dates, reverse=True)


# ++++++++++++++++++++++++++++++++++++++++++++++ тесты, которых вчера не было

async def test_filter_offers_by_candidate_email(offer_repo, test_offer_create_data):
    """Фильтр по части email кандидата"""
    created = await offer_repo.create_offer(test_offer_create_data)

    # Поиск по существующей части email
    filters = OfferFilter(candidate_email="offer_candidate")
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    # Поиск по несуществующей подстроке
    filters = OfferFilter(candidate_email="nonexistent")
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_candidate_status(offer_repo, test_offer_create_data):
    """Фильтр по статусу кандидата (метка)"""
    # Кандидат уже создан в статусе INTERVIEW_PASSED
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(candidate_status=CandidateStatus.INTERVIEW_PASSED)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    # Фильтр по другому статусу – не должно быть
    filters = OfferFilter(candidate_status=CandidateStatus.NEW)
    result = await offer_repo.filter_offers(filters)
    assert created.id not in [o.id for o in result.items]


async def test_filter_offers_by_vacancy_title(offer_repo, test_offer_create_data, test_vacancy):
    """Фильтр по части названия вакансии"""
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(vacancy_title="Test Offer")
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    filters = OfferFilter(vacancy_title="Nonexistent")
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_created_by(offer_repo, test_offer_create_data, test_user):
    """Фильтр по ID создателя оффера"""
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(created_by=test_user.id)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    filters = OfferFilter(created_by=uuid4())
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_created_by_name(offer_repo, test_offer_create_data, test_user):
    """Фильтр по имени создателя (подстрока)"""
    created = await offer_repo.create_offer(test_offer_create_data)

    filters = OfferFilter(created_by_name="Test HR")
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    filters = OfferFilter(created_by_name="Nonexistent")
    result = await offer_repo.filter_offers(filters)
    assert result.total == 0


async def test_filter_offers_by_created_at_range(offer_repo, test_offer_create_data):
    """Фильтр по диапазону created_at (from / to)"""
    created = await offer_repo.create_offer(test_offer_create_data)
    now_sec = int(datetime.now(timezone.utc).timestamp())
    filters = OfferFilter(created_at_from=0, created_at_to=now_sec + 100)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]


async def test_filter_offers_by_start_at_range(offer_repo, test_offer_create_data):
    """Фильтр по диапазону start_at (from / to)"""
    base = test_offer_create_data
    # Создаём оффер с start_at через 30 дней
    created = await offer_repo.create_offer(base)

    now = datetime.now(timezone.utc)
    from_ts = int((now + timedelta(days=29)).timestamp())
    to_ts = int((now + timedelta(days=31)).timestamp())

    filters = OfferFilter(start_at_from=from_ts, start_at_to=to_ts)
    result = await offer_repo.filter_offers(filters)
    assert result.total >= 1
    assert created.id in [o.id for o in result.items]

    # Диапазон, не включающий start_at
    filters = OfferFilter(start_at_from=0, start_at_to=from_ts - 1)
    result = await offer_repo.filter_offers(filters)
    assert created.id not in [o.id for o in result.items]


# ========== Недостающие сортировки ==========

async def test_filter_offers_sorting_by_status(offer_repo, test_offer_create_data):
    """Сортировка по статусу оффера (метке)"""
    base = test_offer_create_data
    # Создаём офферы с разными статусами
    statuses = [OfferStatus.PENDING, OfferStatus.APPROVED_MNG, OfferStatus.REJECTED_MNG]
    created_ids = []
    for st in statuses:
        data = base.model_copy(deep=True)
        data.status = st
        offer = await offer_repo.create_offer(data)
        created_ids.append(offer.id)

    # Сортировка ASC (по алфавиту названий статусов)
    filters = OfferFilter(sort_by="status", sort_order="asc")
    result = await offer_repo.filter_offers(filters)
    statuses_asc = [o.status for o in result.items if o.id in created_ids]
    # Ожидаем: APPROVED_MNG, PENDING, REJECTED_MNG (алфавитный порядок)
    expected = sorted(statuses)
    assert statuses_asc == expected

    # DESC
    filters.sort_order = "desc"
    result = await offer_repo.filter_offers(filters)
    statuses_desc = [o.status for o in result.items if o.id in created_ids]
    assert statuses_desc == sorted(statuses, reverse=True)



# ========== Комбинация фильтров ==========

async def test_filter_offers_combined_status_and_salary(offer_repo, test_offer_create_data):
    """Комбинация фильтров: статус оффера + диапазон зарплаты"""
    base = test_offer_create_data
    # Создаём APPROVED_MNG с зарплатой 100000
    data1 = base.model_copy(deep=True)
    data1.status = OfferStatus.APPROVED_MNG
    data1.salary = 100000
    offer1 = await offer_repo.create_offer(data1)

    # Создаём APPROVED_MNG с зарплатой 200000
    data2 = base.model_copy(deep=True)
    data2.status = OfferStatus.APPROVED_MNG
    data2.salary = 200000
    offer2 = await offer_repo.create_offer(data2)

    # Создаём PENDING с зарплатой 150000 (не должен попасть)
    data3 = base.model_copy(deep=True)
    data3.status = OfferStatus.PENDING
    data3.salary = 150000
    await offer_repo.create_offer(data3)

    # Фильтр: статус APPROVED_MNG и зарплата от 80000 до 150000
    filters = OfferFilter(
        status=OfferStatus.APPROVED_MNG,
        salary_from=80000,
        salary_to=150000
    )
    result = await offer_repo.filter_offers(filters)
    assert result.total == 1
    assert result.items[0].id == offer1.id
    assert offer2.id not in [o.id for o in result.items]