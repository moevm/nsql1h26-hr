from fastapi import APIRouter, status, Depends, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID
from app.core.database import get_db
from app.models.system_backup import SystemBackup
from app.repositories.user_repo import UserRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.repositories.offer_repo import OfferRepository
from app.services.admin_service import AdminService
from app.core.security import require_role

router = APIRouter()


def get_admin_service(driver: AsyncDriver = Depends(get_db)) -> AdminService:
    user_repo = UserRepository(driver)
    vacancy_repo = VacancyRepository(driver)
    test_task_repo = TestTaskRepository(driver)
    candidate_repo = CandidateRepository(driver)
    interview_repo = InterviewRepository(driver)
    offer_repo = OfferRepository(driver)
    return AdminService(
        user_repo,
        vacancy_repo,
        test_task_repo,
        candidate_repo,
        interview_repo,
        offer_repo,
    )


@router.get("/backup", response_model=SystemBackup, status_code=status.HTTP_200_OK)
async def backup(
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(require_role("ADMIN")),
):
    return await admin_service.backup()
