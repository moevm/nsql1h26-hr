from datetime import datetime
from fastapi import status
from uuid import UUID
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate, VacancyResponse, VacancyStatus, VacancyPatch, VacancyFilter, VacancyFilterResponse
from app.core.exceptions import AppError


class VacancyService:
    def __init__(self, vacancy_repo: VacancyRepository):
        self.vacancy_repo = vacancy_repo

    async def create_vacancy(self,
                             vacancy_data: VacancyCreate) -> VacancyResponse:
        if vacancy_data.status is None:
            vacancy_data.status = VacancyStatus.OPEN
        if vacancy_data.status == VacancyStatus.CLOSED or \
                vacancy_data.closed_at is not None:
            raise AppError("Cannot create CLOSED vacancy",
                           status.HTTP_400_BAD_REQUEST)

        vacancy_dict = await self.vacancy_repo.create_vacancy(vacancy_data)
        return VacancyResponse(**vacancy_dict)

    async def get_vacancy_by_id(self,
                                vacancy_id: UUID):
        vacancy_dict = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
        if vacancy_dict is None:
            raise AppError("Vacancy not found", status.HTTP_404_NOT_FOUND)
        return VacancyResponse(**vacancy_dict)

    async def patch_vacancy(self, vacancy_id: UUID, vacancy_data: VacancyPatch) -> VacancyResponse:
        if vacancy_data.status == VacancyStatus.OPEN and vacancy_data.closed_at is not None:
            raise AppError("Invalid vacancy status",
                           status.HTTP_400_BAD_REQUEST)
        if vacancy_data.status is None and vacancy_data.closed_at is not None:
            vacancy_data.status = VacancyStatus.CLOSED
        if vacancy_data.status == VacancyStatus.CLOSED and vacancy_data.closed_at is None:
            vacancy_data.closed_at = datetime.now(timezone.utc)
        data_dict = vacancy_data.model_dump(exclude_unset=True)
        vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise AppError("Vacancy not found", status.HTTP_404_NOT_FOUND)
        if not data_dict:
            return VacancyResponse(**vacancy)
        vacancy = await self.vacancy_repo.patch_vacancy(vacancy_id, data_dict)
        return VacancyResponse(**vacancy)
    

    async def filter_vacancies(self, filters: VacancyFilter) -> VacancyFilterResponse:
        vacancies = await self.vacancy_repo.filter_vacancies(filters)
        return VacancyFilterResponse(**vacancies)
