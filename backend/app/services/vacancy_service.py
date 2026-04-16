from datetime import datetime
from fastapi import status
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate, VacancyResponse, VacancyStatus
from app.core.exceptions import AppError


class VacancyService:
    def __init__(self, vacancy_repo: VacancyRepository):
        self.vacancy_repo = vacancy_repo

    async def create_vacancy(self, vacancy_data: VacancyCreate) -> VacancyResponse:
        if vacancy_data.status is None:
            vacancy_data.status = VacancyStatus.OPEN
        if vacancy_data.status == VacancyStatus.CLOSED or vacancy_data.closed_at is not None:
            raise AppError("Cannot create CLOSED vacancy",
                           status.HTTP_400_BAD_REQUEST)
        if vacancy_data.created_at is None:
            vacancy_data.created_at = datetime.now()
        vacancy_dict = await self.vacancy_repo.create_vacancy(vacancy_data)
        return VacancyResponse(**vacancy_dict)
