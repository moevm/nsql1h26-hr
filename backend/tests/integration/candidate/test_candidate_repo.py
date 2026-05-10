import pytest
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate
from app.models.candidate import (
    CandidateCreate,
    CandidateFilter,
    CandidateSort,
    CandidateStatus,
)
from app.models.helpers import SortOrder


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


async def test_create_candidate_no_vacancy(
    candidate_repo, test_task_repo, vacancy_repo
):
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


async def test_create_candidate_no_test_task(
    candidate_repo, test_task_repo, vacancy_repo
):
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
        vacancy_id=vacancy_id,
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
        status="NEW",
    )
    created = await candidate_repo.create_candidate(candidate)
    assert created is not None
    assert created["full_name"] == candidate.full_name
    assert created["email"] == candidate.email
    assert created["phone"] == candidate.phone
    assert created["status"] == candidate.status


async def test_get_candidate_all(candidate_repo, test_task_repo, vacancy_repo):
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
    got = await candidate_repo.get_candidate_by_id(created["id"])
    assert got == created


async def test_get_candidate_solo(candidate_repo):
    candidate = CandidateCreate(
        full_name="Candidate A",
        email="candidate@gmail.com",
        phone="+79527416565",
        status="NEW",
        resume_url="https://google.com/",
    )
    created = await candidate_repo.create_candidate(candidate)
    got = await candidate_repo.get_candidate_by_id(created["id"])
    assert got == created


async def test_filter_by_full_name_substring(
    candidate_repo, vacancy_repo, test_task_repo
):
    vacancy = await vacancy_repo.create_vacancy(
        VacancyCreate(title="V1", description="D1")
    )
    vacancy_id = vacancy["id"]
    test_task = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Test", test_task_url="http://test.com", vacancy_id=vacancy_id
        )
    )
    test_task_id = test_task["id"]

    candidate1 = CandidateCreate(
        full_name="Ivan Ivanovich",
        email="ivan@example.com",
        phone="+79123456789",
        status="NEW",
        resume_url="http://resume1.com",
        vacancy_id=vacancy_id,
        test_task_id=test_task_id,
    )
    candidate2 = CandidateCreate(
        full_name="Petr Ivanov",
        email="petr@example.com",
        phone="+79998887766",
        status="NEW",
        resume_url="http://resume2.com",
        vacancy_id=vacancy_id,
        test_task_id=test_task_id,
    )
    await candidate_repo.create_candidate(candidate1)
    await candidate_repo.create_candidate(candidate2)

    filters = CandidateFilter(full_name="petr")
    result = await candidate_repo.filter_candidates(filters)

    assert result["total"] == 1
    assert result["items"][0]["full_name"] == "Petr Ivanov"


async def test_filter_by_vacancy_title(candidate_repo, vacancy_repo, test_task_repo):
    vacancy1 = await vacancy_repo.create_vacancy(
        VacancyCreate(title="Backend Python", description="D1")
    )
    vacancy2 = await vacancy_repo.create_vacancy(
        VacancyCreate(title="Frontend JS", description="D2")
    )
    test_task1 = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Test1", test_task_url="http://1.com", vacancy_id=vacancy1["id"]
        )
    )
    test_task2 = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Test2", test_task_url="http://2.com", vacancy_id=vacancy2["id"]
        )
    )

    candidate1 = CandidateCreate(
        full_name="C1",
        email="c1@ex.com",
        phone="+79638527474",
        status="NEW",
        resume_url="http://r1.com",
        vacancy_id=vacancy1["id"],
        test_task_id=test_task1["id"],
    )
    candidate2 = CandidateCreate(
        full_name="C2",
        email="c2@ex.com",
        phone="+79638527474",
        status="NEW",
        resume_url="http://r2.com",
        vacancy_id=vacancy2["id"],
        test_task_id=test_task2["id"],
    )
    await candidate_repo.create_candidate(candidate1)
    await candidate_repo.create_candidate(candidate2)

    filters = CandidateFilter(vacancy_title="python")
    result = await candidate_repo.filter_candidates(filters)
    assert result["total"] == 1
    assert result["items"][0]["full_name"] == "C1"


async def test_filter_by_test_task_title(candidate_repo, vacancy_repo, test_task_repo):
    vacancy = await vacancy_repo.create_vacancy(
        VacancyCreate(title="V", description="D")
    )
    vacancy_id = vacancy["id"]

    tt1 = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Python basics", test_task_url="http://py.com", vacancy_id=vacancy_id
        )
    )
    tt2 = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="JS advanced", test_task_url="http://js.com", vacancy_id=vacancy_id
        )
    )

    candidate1 = CandidateCreate(
        full_name="Py Dev",
        email="py@ex.com",
        phone="+79638527474",
        status="NEW",
        resume_url="http://r1.com",
        vacancy_id=vacancy_id,
        test_task_id=tt1["id"],
    )
    candidate2 = CandidateCreate(
        full_name="JS Dev",
        email="js@ex.com",
        phone="+79638527474",
        status="NEW",
        resume_url="http://r2.com",
        vacancy_id=vacancy_id,
        test_task_id=tt2["id"],
    )
    await candidate_repo.create_candidate(candidate1)
    await candidate_repo.create_candidate(candidate2)

    filters = CandidateFilter(test_task_title="basics")
    result = await candidate_repo.filter_candidates(filters)
    assert result["total"] == 1
    assert result["items"][0]["full_name"] == "Py Dev"


async def test_sorting_and_pagination(candidate_repo, vacancy_repo, test_task_repo):
    vacancy = await vacancy_repo.create_vacancy(
        VacancyCreate(title="V", description="D")
    )
    vacancy_id = vacancy["id"]
    test_task = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Test", test_task_url="http://test.com", vacancy_id=vacancy_id
        )
    )
    test_task_id = test_task["id"]

    names = ["Clara", "Anna", "Boris"]
    for name in names:
        candidate = CandidateCreate(
            full_name=name,
            email=f"{name.lower()}@ex.com",
            phone="+79638527474",
            status="NEW",
            resume_url="http://r.com",
            vacancy_id=vacancy_id,
            test_task_id=test_task_id,
        )
        await candidate_repo.create_candidate(candidate)

    filters = CandidateFilter(
        sort_by=CandidateSort.FULL_NAME, sort_order=SortOrder.ASC, limit=2, offset=0
    )
    result = await candidate_repo.filter_candidates(filters)
    assert result["total"] == 3
    assert len(result["items"]) == 2
    assert result["items"][0]["full_name"] == "Anna"
    assert result["items"][1]["full_name"] == "Boris"

    filters = CandidateFilter(
        sort_by=CandidateSort.FULL_NAME, sort_order=SortOrder.DESC, limit=2, offset=1
    )
    result = await candidate_repo.filter_candidates(filters)
    assert len(result["items"]) == 2
    assert result["items"][0]["full_name"] == "Boris"
    assert result["items"][1]["full_name"] == "Anna"


async def test_sorting_by_status(candidate_repo, vacancy_repo, test_task_repo):
    vacancy = await vacancy_repo.create_vacancy(
        VacancyCreate(title="V", description="D")
    )
    vacancy_id = vacancy["id"]
    test_task = await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Test", test_task_url="http://test.com", vacancy_id=vacancy_id
        )
    )
    test_task_id = test_task["id"]

    candidates = [
        {"status": "TEST", "name": "Boris"},
        {"status": "OFFER", "name": "Anna"},
        {"status": "NEW", "name": "Clara"},
    ]
    candidate_id = ""
    for cand in candidates:
        candidate = CandidateCreate(
            full_name=cand["name"],
            email=f"{cand["name"].lower()}@ex.com",
            phone="+79638527474",
            status=cand["status"],
            resume_url="http://r.com",
            vacancy_id=vacancy_id,
            test_task_id=test_task_id,
        )
        await candidate_repo.create_candidate(candidate)
    filters = CandidateFilter(
        sort_by=CandidateSort.STATUS, sort_order=SortOrder.ASC, limit=3, offset=0
    )
    result = await candidate_repo.filter_candidates(filters)
    assert result["total"] == 3
    assert len(result["items"]) == 3
    assert result["items"][0]["status"] == "NEW"
    assert result["items"][1]["status"] == "OFFER"
    assert result["items"][2]["status"] == "TEST"

    filters = CandidateFilter(
        sort_by=CandidateSort.STATUS, sort_order=SortOrder.DESC, limit=3, offset=0
    )
    result = await candidate_repo.filter_candidates(filters)
    assert result["total"] == 3
    assert len(result["items"]) == 3
    assert result["items"][2]["status"] == "NEW"
    assert result["items"][1]["status"] == "OFFER"
    assert result["items"][0]["status"] == "TEST"


async def test_patch_candidate_simple(candidate_repo, test_task_repo, vacancy_repo):
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
    candidate_id = (await candidate_repo.create_candidate(candidate))["id"]
    patch = {"full_name": "Candidate A", "email": "candidate@gmail.com"}
    patched_candidate = await candidate_repo.patch_candidate(candidate_id, patch)
    assert patched_candidate["id"] == candidate_id
    assert patched_candidate["full_name"] == patch["full_name"]
    assert patched_candidate["email"] == patch["email"]
    assert patched_candidate["full_name"] == patch["full_name"]
    assert patched_candidate["phone"] == candidate.phone
    assert patched_candidate["status"] == candidate.status
    assert patched_candidate["resume_url"] == str(candidate.resume_url)
    assert patched_candidate["vacancy_id"] == str(candidate.vacancy_id)
    assert patched_candidate["test_task_id"] == str(candidate.test_task_id)


async def test_patch_candidate_status(candidate_repo, test_task_repo, vacancy_repo):
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
    candidate_id = (await candidate_repo.create_candidate(candidate))["id"]
    patch = {
        "full_name": "Candidate A",
        "email": "candidate@gmail.com",
        "status": "TEST",
    }
    patched_candidate = await candidate_repo.patch_candidate(candidate_id, patch)
    assert patched_candidate["id"] == candidate_id
    assert patched_candidate["full_name"] == patch["full_name"]
    assert patched_candidate["email"] == patch["email"]
    assert patched_candidate["full_name"] == patch["full_name"]
    assert patched_candidate["phone"] == candidate.phone
    assert patched_candidate["status"] == "TEST"
    assert patched_candidate["resume_url"] == str(candidate.resume_url)
    assert patched_candidate["vacancy_id"] == str(candidate.vacancy_id)
    assert patched_candidate["test_task_id"] == str(candidate.test_task_id)


async def test_patch_candidate_ids(candidate_repo, test_task_repo, vacancy_repo):
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
    )
    candidate_id = (await candidate_repo.create_candidate(candidate))["id"]
    patch = {"vacancy_id": str(vacancy_id), "test_task_id": str(test_task_id)}
    patched_candidate = await candidate_repo.patch_candidate(candidate_id, patch)
    assert patched_candidate["id"] == candidate_id
    assert patched_candidate["full_name"] == candidate.full_name
    assert patched_candidate["email"] == candidate.email
    assert patched_candidate["phone"] == candidate.phone
    assert patched_candidate["status"] == candidate.status
    assert patched_candidate["resume_url"] == str(candidate.resume_url)
    assert patched_candidate["vacancy_id"] == str(vacancy_id)
    assert patched_candidate["test_task_id"] == str(test_task_id)
