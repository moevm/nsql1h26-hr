from fastapi import APIRouter, status, Depends, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID
from app.core.database import get_db
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.services.candidate_service import CandidateService
from app.models.candidate import CandidateCreate, CandidateResponse, CandidateFilterResponse, CandidateFilter
from app.core.security import require_role


router = APIRouter()


def get_candidate_service(driver: AsyncDriver = Depends(get_db)) -> CandidateService:
    vacancy_repo = VacancyRepository(driver)
    test_task_repo = TestTaskRepository(driver)
    candidate_repo = CandidateRepository(driver)
    return CandidateService(test_task_repo, vacancy_repo, candidate_repo)


@router.post("",
             response_model=CandidateResponse,
             status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: dict = Depends(require_role('HR'))
):
    candidate = await candidate_service.create_candidate(candidate_data)
    return candidate


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    status_code=status.HTTP_200_OK
)
async def get_test_task_by_id(
    candidate_id: UUID,
    candidate_service: CandidateService = Depends(get_candidate_service),
):
    candidate = await candidate_service.get_candidate_by_id(candidate_id)
    return candidate


@router.get(
    "",
    response_model=CandidateFilterResponse,
    status_code=status.HTTP_200_OK
)
async def filter_test_tasks(
    filters: Annotated[CandidateFilter, Query()],
    candidate_service: CandidateService = Depends(get_candidate_service),
):
    candidates = await candidate_service.filter_candidates(filters)
    return candidates
