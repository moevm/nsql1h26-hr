#!/usr/bin/env python3
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Neo4jDB
from app.core.config import settings

from app.models.system_backup import SystemBackup

from app.repositories.user_repo import UserRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.repositories.offer_repo import OfferRepository
from app.repositories.admin_repo import AdminRepository

from app.services.admin_service import AdminService


async def seed():
    await Neo4jDB.connect()
    driver = Neo4jDB.get_driver()

    user_repo = UserRepository(driver)
    vacancy_repo = VacancyRepository(driver)
    test_task_repo = TestTaskRepository(driver)
    candidate_repo = CandidateRepository(driver)
    interview_repo = InterviewRepository(driver)
    offer_repo = OfferRepository(driver)
    admin_repo = AdminRepository(driver)

    service = AdminService(
        user_repo,
        vacancy_repo,
        test_task_repo,
        candidate_repo,
        interview_repo,
        offer_repo,
        admin_repo
    )

    is_empty = await service.is_empty()
    if is_empty:
        with open('backup.json', 'r', encoding='utf-8') as f:
            backup = SystemBackup.model_validate_json(f.read())
        await service.restore(backup)
        print('DB Restored successfully')
    else:
        print('Database not empty, skipping initialization')

    await Neo4jDB.close()


if __name__ == "__main__":
    asyncio.run(seed())
