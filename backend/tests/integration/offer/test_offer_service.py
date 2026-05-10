import pytest
from fastapi import status
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from app.models.offer import OfferCreate, OfferStatus, OfferFilter, OfferPatch
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate, VacancyStatus
from app.models.user import UserCreate, Role
from app.core.exceptions import AppError


@pytest.fixture
async def test_user(user_service):
    user = await user_service.create_user(
        UserCreate(
            email=f"hr_{uuid4()}@example.com",
            full_name="Test HR",
            password="hash123456",
            role=Role.HR,
        )
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


async def test_create_offer_ok(offer_service, test_offer_create_data):
    offer = await offer_service.create_offer(test_offer_create_data)
    assert offer is not None
    assert offer.id is not None


async def test_patch_offer_hired(
    offer_service, candidate_service, vacancy_service, test_offer_create_data
):
    offer = await offer_service.create_offer(test_offer_create_data)
    patched_offer = await offer_service.patch_offer(
        offer.id, OfferPatch(status=OfferStatus.APPROVED_CND)
    )
    assert patched_offer.status == OfferStatus.APPROVED_CND
    vacancy = await vacancy_service.get_vacancy_by_id(offer.vacancy_id)
    assert vacancy.status == VacancyStatus.CLOSED
    candidate = await candidate_service.get_candidate_by_id(offer.candidate_id)
    assert candidate.status == CandidateStatus.HIRED


async def test_patch_offer_rejected_cnf(
    offer_service, candidate_service, vacancy_service, test_offer_create_data
):
    offer = await offer_service.create_offer(test_offer_create_data)
    patched_offer = await offer_service.patch_offer(
        offer.id, OfferPatch(status=OfferStatus.REJECTED_CNF)
    )
    assert patched_offer.status == OfferStatus.REJECTED_CNF
    candidate = await candidate_service.get_candidate_by_id(offer.candidate_id)
    assert candidate.status == CandidateStatus.REJECTED


async def test_patch_offer_rejected_mng(
    offer_service, candidate_service, vacancy_service, test_offer_create_data
):
    offer = await offer_service.create_offer(test_offer_create_data)
    patched_offer = await offer_service.patch_offer(
        offer.id, OfferPatch(status=OfferStatus.REJECTED_MNG)
    )
    assert patched_offer.status == OfferStatus.REJECTED_MNG
    candidate = await candidate_service.get_candidate_by_id(offer.candidate_id)
    assert candidate.status == CandidateStatus.REJECTED


async def test_create_offer_updates_status(
    offer_service, test_offer_create_data, candidate_repo
):
    """После создания оффера статус кандидата должен стать OFFER"""
    candidate_id = test_offer_create_data.candidate_id

    # Проверяем статус ДО
    candidate_before = await candidate_repo.get_candidate_by_id(candidate_id)
    assert candidate_before["status"] == CandidateStatus.INTERVIEW_PASSED

    # Создаём оффер
    offer = await offer_service.create_offer(test_offer_create_data)
    assert offer is not None

    # Проверяем статус ПОСЛЕ
    candidate_after = await candidate_repo.get_candidate_by_id(candidate_id)
    assert candidate_after["status"] == CandidateStatus.OFFER


async def test_get_offer_by_id_ok(offer_service, test_offer_create_data):
    created = await offer_service.create_offer(test_offer_create_data)
    fetched = await offer_service.get_offer_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_offer_by_id_not_found(offer_service):
    with pytest.raises(AppError) as ex:
        await offer_service.get_offer_by_id(uuid4())
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND


async def test_create_offer_candidate_not_found(offer_service, test_user, test_vacancy):
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    offer_data = OfferCreate(
        candidate_id=uuid4(),  # несуществующий ID
        vacancy_id=UUID(test_vacancy["id"]),
        created_by=test_user.id,
        salary=100000,
        start_at=start_at,
    )
    with pytest.raises(AppError) as ex:
        await offer_service.create_offer(offer_data)
        assert ex.value.args[1] == status.HTTP_400_BAD_REQUEST


async def test_create_offer_vacancy_not_found(offer_service, test_user, test_candidate):
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    offer_data = OfferCreate(
        candidate_id=test_candidate["id"],
        vacancy_id=uuid4(),  # несуществующий ID
        created_by=test_user.id,
        salary=100000,
        start_at=start_at,
    )
    with pytest.raises(AppError) as ex:
        await offer_service.create_offer(offer_data)
        assert ex.value.args[1] == status.HTTP_400_BAD_REQUEST


async def test_get_offer_by_id_not_found(offer_service):
    with pytest.raises(AppError) as ex:
        await offer_service.get_offer_by_id(uuid4())
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND

async def test_filter_offers_basic(offer_service, test_offer_create_data):
    created = await offer_service.create_offer(test_offer_create_data)

    # Фильтр без параметров
    filters = OfferFilter()
    result = await offer_service.filter_offers(filters)
    assert result.total >= 1
    assert any(item.id == created.id for item in result.items)

    # Фильтр по candidate_id
    filters = OfferFilter(candidate_id=created.candidate_id)
    result = await offer_service.filter_offers(filters)
    assert result.total >= 1
    assert all(item.candidate_id == created.candidate_id for item in result.items)

    # Фильтр по несуществующему candidate_id – пустой результат
    filters = OfferFilter(candidate_id=uuid4())
    result = await offer_service.filter_offers(filters)
    assert result.total == 0