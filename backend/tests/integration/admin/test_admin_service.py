import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import UserCreate, Role
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate
from app.models.candidate import CandidateCreate, CandidateStatus
from app.models.interview import InterviewCreate, InterviewResult, InterviewPatch
from app.models.offer import OfferCreate, OfferStatus


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
    return user


async def test_backup(
    tech_spec_user,
    admin_service,
    vacancy_service,
    test_task_service,
    candidate_service,
    interview_service,
    offer_service,
):
    vacancy = await vacancy_service.create_vacancy(
        VacancyCreate(title="Test vacancy", description="Test Vacancy Description")
    )
    test_task = await test_task_service.create_test_task(
        TestTaskCreate(
            title="test task 1",
            test_task_url="https://google.com",
            vacancy_id=vacancy.id,
        )
    )
    candidate = await candidate_service.create_candidate(
        CandidateCreate(
            full_name="Candidate A",
            email="candidate@gmail.com",
            phone="+79638527411",
            resume_url="https://google.com",
            status=CandidateStatus.NEW,
            vacancy_id=vacancy.id,
            test_task_id=test_task.id,
        )
    )
    interview = await interview_service.create_interview(
        InterviewCreate(
            candidate_id=candidate.id,
            tech_spec_id=tech_spec_user.id,
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            zoom_url="https://zoom.us/test",
            feedback=None,
            result=InterviewResult.AWAIT_INTERVIEW,
        )
    )
    interview = await interview_service.patch_interview(
        interview.id,
        InterviewPatch(result=InterviewResult.INTERVIEW_PASSED, feedback="good"),
    )
    offer = await offer_service.create_offer(
        OfferCreate(
            candidate_id=candidate.id,
            vacancy_id=vacancy.id,
            created_by=tech_spec_user.id,
            salary=100000,
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            status=OfferStatus.PENDING,
        )
    )
    candidate = await candidate_service.get_candidate_by_id(candidate.id)

    backup = await admin_service.backup()

    assert len(backup.users) == 1
    assert backup.users[0] == tech_spec_user

    assert len(backup.vacancies) == 1
    assert backup.vacancies[0] == vacancy

    assert len(backup.test_tasks) == 1
    assert backup.test_tasks[0] == test_task

    assert len(backup.candidates) == 1
    assert backup.candidates[0] == candidate

    assert len(backup.interviews) == 1
    assert backup.interviews[0] == interview

    assert len(backup.offers) == 1
    assert backup.offers[0] == offer
