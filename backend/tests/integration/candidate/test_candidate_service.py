import pytest
import uuid
from fastapi import status
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate
from app.models.candidate import (
    CandidateCreate,
    CandidatePatch,
    CandidateFilter,
    CandidateFilterResponse,
    CandidateStatus,
)
from app.core.exceptions import AppError


async def test_create_candidate_ok(
    candidate_service, test_task_service, vacancy_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    got_candidate = await candidate_service.create_candidate(candidate)

    assert got_candidate is not None
    assert got_candidate.id is not None
    assert got_candidate.full_name == candidate.full_name
    assert got_candidate.email == candidate.email
    assert got_candidate.phone == candidate.phone
    assert got_candidate.status == candidate.status
    assert got_candidate.resume_url == candidate.resume_url
    assert got_candidate.vacancy_id == candidate.vacancy_id
    assert got_candidate.test_task_id == candidate.test_task_id


async def test_create_bad_vacancy(candidate_service):
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=uuid.uuid4(),
    )
    with pytest.raises(AppError, match=r"vacancy"):
        await candidate_service.create_candidate(candidate)


async def test_create_bad_test_task(candidate_service):
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        test_task_id=uuid.uuid4(),
    )
    with pytest.raises(AppError, match=r"test task"):
        await candidate_service.create_candidate(candidate)


async def test_create_bad_vacancy_test_task(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy1 = await vacancy_service.create_vacancy(test_vacancy)
    vacancy2 = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy1.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        test_task_id=test_task.id,
        vacancy_id=vacancy2.id,
    )
    with pytest.raises(AppError, match=r"Test task is not for given vacancy"):
        await candidate_service.create_candidate(candidate)


async def test_get_candidate_by_id_ok(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    created_candidate = await candidate_service.create_candidate(candidate)

    got_candidate = await candidate_service.get_candidate_by_id(created_candidate.id)
    assert got_candidate == created_candidate


async def test_filter_candidates(candidate_service, vacancy_service, test_task_service):
    vacancy = await vacancy_service.create_vacancy(
        VacancyCreate(title="Test Vacancy", description="Desc")
    )
    test_task = await test_task_service.create_test_task(
        TestTaskCreate(
            title="Test Task", test_task_url="https://test.com", vacancy_id=vacancy.id
        )
    )
    candidates_data = [
        CandidateCreate(
            full_name="Candidate A",
            email="a@example.com",
            phone="+79123456789",
            status="NEW",
            resume_url="https://resume1.com",
            vacancy_id=vacancy.id,
            test_task_id=test_task.id,
        ),
        CandidateCreate(
            full_name="Candidate B",
            email="b@example.com",
            phone="+79998887766",
            status="NEW",
            resume_url="https://resume2.com",
            vacancy_id=vacancy.id,
            test_task_id=test_task.id,
        ),
    ]
    created_candidates = []
    for cand_data in candidates_data:
        created = await candidate_service.create_candidate(cand_data)
        created_candidates.append(created)

    filters = CandidateFilter()
    result = await candidate_service.filter_candidates(filters)
    assert result.total == len(candidates_data)


async def test_patch_candidate_ok(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    test_vacancy2 = VacancyCreate(
        title="Test vacancy2", description="Test Vacancy Description2"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    vacancy2 = await vacancy_service.create_vacancy(test_vacancy2)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    candidate_id = (await candidate_service.create_candidate(candidate)).id
    patch = CandidatePatch(
        full_name="Candidate B",
        email="candidate_b@gmail.com",
        vacancy_id=vacancy2.id,
        status="OFFER",
    )
    got_candidate = await candidate_service.patch_candidate(candidate_id, patch)
    assert got_candidate is not None
    assert got_candidate.id is not None
    assert got_candidate.full_name == patch.full_name
    assert got_candidate.email == patch.email
    assert got_candidate.phone == candidate.phone
    assert got_candidate.status == "OFFER"
    assert got_candidate.resume_url == candidate.resume_url
    assert got_candidate.vacancy_id == vacancy2.id
    assert got_candidate.test_task_id == candidate.test_task_id


async def test_patch_candidate_bad_id(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    (await candidate_service.create_candidate(candidate)).id
    patch = CandidatePatch(
        full_name="Candidate B", email="candidate_b@gmail.com", status="OFFER"
    )
    with pytest.raises(AppError) as ex:
        await candidate_service.patch_candidate(uuid.uuid4(), patch)
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND


async def test_patch_candidate_bad_vacancy_id(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    candidate_id = (await candidate_service.create_candidate(candidate)).id
    patch = CandidatePatch(
        full_name="Candidate B",
        email="candidate_b@gmail.com",
        status="OFFER",
        vacancy_id=uuid.uuid4(),
    )
    with pytest.raises(AppError) as ex:
        await candidate_service.patch_candidate(candidate_id, patch)
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND


async def test_patch_candidate_bad_test_task_id(
    candidate_service, vacancy_service, test_task_service
):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    test_task = await test_task_service.create_test_task(test_task)
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79638527411",
        resume_url="https://google.com",
        status=CandidateStatus.NEW,
        vacancy_id=vacancy.id,
        test_task_id=test_task.id,
    )
    candidate_id = (await candidate_service.create_candidate(candidate)).id
    patch = CandidatePatch(
        full_name="Candidate B",
        email="candidate_b@gmail.com",
        status="OFFER",
        test_task_id=uuid.uuid4(),
    )
    with pytest.raises(AppError) as ex:
        await candidate_service.patch_candidate(candidate_id, patch)
        assert ex.value.args[1] == status.HTTP_404_NOT_FOUND
