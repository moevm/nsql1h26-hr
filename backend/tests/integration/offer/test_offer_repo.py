import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from app.models.offer import OfferCreate, OfferStatus
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.vacancy import VacancyCreate
from app.models.user import UserCreate, Role
from app.repositories.offer_repo import OfferRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.user_repo import UserRepository


@pytest.fixture
async def user_repo(neo4j_driver):
    return UserRepository(neo4j_driver)


@pytest.fixture
async def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


@pytest.fixture
async def candidate_repo(neo4j_driver):
    return CandidateRepository(neo4j_driver)


@pytest.fixture
async def offer_repo(neo4j_driver):
    return OfferRepository(neo4j_driver)


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

async def test_create_offer_candidate_not_found(offer_repo, test_user, test_vacancy):
    """Создание оффера для несуществующего кандидата должно вернуть None"""
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    offer_data = OfferCreate(
        candidate_id=uuid4(),  # несуществующий ID
        vacancy_id=UUID(test_vacancy["id"]),
        created_by=test_user.id,
        salary=100000,
        start_at=start_at,
    )
    offer = await offer_repo.create_offer(offer_data)
    assert offer is None


async def test_create_offer_vacancy_not_found(offer_repo, test_user, test_candidate):
    """Создание оффера для несуществующей вакансии должно вернуть None"""
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    offer_data = OfferCreate(
        candidate_id=test_candidate["id"],
        vacancy_id=uuid4(),  # несуществующий ID
        created_by=test_user.id,
        salary=100000,
        start_at=start_at,
    )
    offer = await offer_repo.create_offer(offer_data)
    assert offer is None

async def test_get_offer_by_id_ok(offer_repo, test_offer_create_data):
    created = await offer_repo.create_offer(test_offer_create_data)
    fetched = await offer_repo.get_offer_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_offer_by_id_not_found(offer_repo):
    assert await offer_repo.get_offer_by_id(uuid4()) is None