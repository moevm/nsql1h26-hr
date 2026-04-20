from fastapi import APIRouter, Depends, status, Query
from neo4j import AsyncDriver
from uuid import UUID
from typing import Annotated

from app.core.database import get_db
from app.services.vacancy_service import VacancyService
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate, VacancyPatch, VacancyResponse, VacancyFilter, VacancyFilterResponse
from app.core.exceptions import AppError
from app.core.security import require_role

router = APIRouter()


def get_vacancy_service(driver: AsyncDriver = Depends(get_db)) -> VacancyService:
    vacancy_repo = VacancyRepository(driver)
    return VacancyService(vacancy_repo)


@router.post("", response_model=VacancyResponse,
             status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
    current_user: dict = Depends(require_role('HR'))
):
    vacancy = await vacancy_service.create_vacancy(vacancy_data)
    if not vacancy:
        raise AppError(
            "Unable to create vacancy", status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return vacancy


@router.get("/{vacancy_id}",
            response_model=VacancyResponse,
            status_code=status.HTTP_200_OK)
async def get_vacancy_by_id(
    vacancy_id: UUID,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
):
    vacancy = await vacancy_service.get_vacancy_by_id(vacancy_id)
    if not vacancy:
        raise AppError("Vacancy not found", status.HTTP_404_NOT_FOUND)
    return vacancy


@router.patch("/{vacancy_id}",
              response_model=VacancyResponse,
              status_code=status.HTTP_200_OK)
async def patch_vacancy(
        vacancy_id: UUID,
        patch_data: VacancyPatch,
        vacancy_service: VacancyService = Depends(get_vacancy_service),
        current_user: dict = Depends(require_role('HR'))
        ):
    vacancy = await vacancy_service.patch_vacancy(vacancy_id, patch_data)
    if not vacancy:
        raise AppError("Vacancy not found", status.HTTP_404_NOT_FOUND)
    return vacancy


@router.get("", 
            response_model=VacancyFilterResponse,
            status_code=status.HTTP_200_OK)
async def filter_vacancies(
        filters: Annotated[VacancyFilter, Query()], 
        vacancy_service: VacancyService = Depends(get_vacancy_service),
        ):
    vacancies = await vacancy_service.filter_vacancies(filters)
    return vacancies
