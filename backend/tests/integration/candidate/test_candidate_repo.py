import pytest
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate
from app.models.candidate import CandidateCreate


@pytest.fixture
def candidate_repo(neo4j_driver):
    return CandidateRepository(neo4j_driver)


@pytest.fixture
def test_task_repo(neo4j_driver):
    return TestTaskRepository(neo4j_driver)


@pytest.fixture
def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


async def test_create_candidate_all(candidate_repo, test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task_id = (
        await test_task_repo.create_test_task(
            TestTaskCreate(
                title="Test title 1",
                test_task_url="https://google.com",
                vacancy_id=vacancy_id,
            )
        )
    )["id"]

    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW",
        resume_url="https://google.com/",
        vacancy_id=vacancy_id,
        test_task_id=test_task_id,
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["id"] is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status
    assert created["resume_url"] == str(candidate.resume_url)
    assert created["vacancy_id"] == str(candidate.vacancy_id)
    assert created["test_task_id"] == str(candidate.test_task_id)



async def test_create_candidate_no_vacancy(candidate_repo, test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task_id = (
        await test_task_repo.create_test_task(
            TestTaskCreate(
                title="Test title 1",
                test_task_url="https://google.com",
                vacancy_id=vacancy_id,
            )
        )
    )["id"]

    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW",
        resume_url="https://google.com/",
        test_task_id=test_task_id,
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status
    assert created["resume_url"] == str(candidate.resume_url)
    assert created["test_task_id"] == str(candidate.test_task_id)


async def test_create_candidate_no_test_task(candidate_repo, test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]

    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW",
        resume_url="https://google.com/",
        vacancy_id=vacancy_id
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status
    assert created["resume_url"] == str(candidate.resume_url)
    assert created["vacancy_id"] == str(candidate.vacancy_id)


async def test_create_candidate_no_resume(candidate_repo, test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task_id = (
        await test_task_repo.create_test_task(
            TestTaskCreate(
                title="Test title 1",
                test_task_url="https://google.com",
                vacancy_id=vacancy_id,
            )
        )
    )["id"]

    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW",
        vacancy_id=vacancy_id,
        test_task_id=test_task_id,
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status
    assert created["vacancy_id"] == str(candidate.vacancy_id)
    assert created["test_task_id"] == str(candidate.test_task_id)


async def test_create_candidate_solo(candidate_repo, test_task_repo, vacancy_repo):
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW"
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status
