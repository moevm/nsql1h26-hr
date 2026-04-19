from fastapi import APIRouter, status, Depends, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID
from app.core.database import get_db
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.services.candidate_service import CandidateService
from app.models.candidate import CandidateCreate, CandidateResponse


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
    candidate_service: CandidateService = Depends(get_candidate_service)
):
    candidate = await candidate_service.create_candidate(candidate_data)
    return candidate
