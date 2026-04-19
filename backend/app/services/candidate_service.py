from app.repositories.candidate_repo import CandidateRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.candidate import CandidateCreate, CandidateResponse, CandidateStatus
from app.core.exceptions import AppError
from fastapi import status
from uuid import UUID


class CandidateService:
    def __init__(
            self,
            test_task_repo: TestTaskRepository,
            vacancy_repo: VacancyRepository,
            candidate_repo: CandidateRepository
    ):
        self.test_task_repo = test_task_repo
        self.vacancy_repo = vacancy_repo
        self.candidate_repo = candidate_repo

    async def create_candidate(self, candidate_data: CandidateCreate) -> CandidateResponse:
        if candidate_data.vacancy_id:
            vacancy = await self.vacancy_repo.get_vacancy_by_id(candidate_data.vacancy_id)
            if not vacancy:
                raise AppError("Cannot find vacancy with given UUID",
                               status.HTTP_400_BAD_REQUEST)
        if candidate_data.test_task_id:
            test_task = await self.test_task_repo.get_test_task_by_id(candidate_data.test_task_id)
            if not test_task:
                raise AppError("Cannot find test task with given UUID",
                               status.HTTP_400_BAD_REQUEST)
            if candidate_data.vacancy_id and str(candidate_data.vacancy_id) != test_task["vacancy_id"]:
                raise AppError("Test task is not for given vacancy",
                               status.HTTP_400_BAD_REQUEST)
        if candidate_data.status != CandidateStatus.NEW:
            raise AppError("Candidate status must be NEW",
                           status.HTTP_400_BAD_REQUEST)
        candidate = await self.candidate_repo.create_candidate(candidate_data)
        return CandidateResponse(**candidate)

    async def get_candidate_by_id(self, candidate_id: UUID) -> CandidateResponse:
        candidate = await self.candidate_repo.get_candidate_by_id(candidate_id)
        if candidate is None:
            raise AppError("Candidate not found",
                           status.HTTP_404_NOT_FOUND)
        return CandidateResponse(**candidate)
