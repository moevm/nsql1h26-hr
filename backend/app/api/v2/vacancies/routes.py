from fastapi import APIRouter, Depends, status
from neo4j import AsyncDriver

from app.core.database import get_db
from app.services.vacancy_service import VacancyService
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate, VacancyResponse
from app.core.exceptions import AppError

router = APIRouter()


def get_vacancy_service(
        driver: AsyncDriver = Depends(get_db)
        ) -> VacancyService:
    vacancy_repo = VacancyRepository(driver)
    return VacancyService(vacancy_repo)


@router.post("",
             response_model=VacancyResponse,
             status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
):
    vacancy = await vacancy_service.create_vacancy(vacancy_data)
    if not vacancy:
        raise AppError(
            "Unable to create vacancy", status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return vacancy
