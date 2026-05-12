from app.models.system_backup import SystemBackup
from app.models.user import UserFilter
from app.models.vacancy import VacancyFilter
from app.models.test_task import TestTasksFilter
from app.models.candidate import CandidateFilter
from app.models.interview import InterviewFilter
from app.models.offer import OfferFilter
from app.repositories.user_repo import UserRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.repositories.offer_repo import OfferRepository
from app.repositories.admin_repo import AdminRepository


class AdminService:
    def __init__(
        self,
        user_repo: UserRepository,
        vacancy_repo: VacancyRepository,
        test_task_repo: TestTaskRepository,
        candidate_repo: CandidateRepository,
        interview_repo: InterviewRepository,
        offer_repo: OfferRepository,
        admin_repo: AdminRepository
    ):
        self.user_repo = user_repo
        self.vacancy_repo = vacancy_repo
        self.test_task_repo = test_task_repo
        self.candidate_repo = candidate_repo
        self.interview_repo = interview_repo
        self.offer_repo = offer_repo
        self.admin_repo = admin_repo

    async def backup(self) -> SystemBackup:
        users = await self.user_repo.get_users()
        vacancies = (await self.vacancy_repo.filter_vacancies(VacancyFilter()))["items"]
        test_tasks = (await self.test_task_repo.filter_test_tasks(TestTasksFilter()))[
            "items"
        ]
        candidates = (await self.candidate_repo.filter_candidates(CandidateFilter()))[
            "items"
        ]
        interviews = (
            await self.interview_repo.filter_interviews(InterviewFilter())
        ).items
        offers = (await self.offer_repo.filter_offers(OfferFilter())).items

        return SystemBackup(
            users=users,
            vacancies=vacancies,
            test_tasks=test_tasks,
            candidates=candidates,
            interviews=interviews,
            offers=offers,
        )

    async def restore(self, data_backup: SystemBackup) -> None:
        await self.admin_repo.erase_all()
        for user in data_backup.users:
            await self.user_repo.restore_user(user)
        for vacancy in data_backup.vacancies:
            await self.vacancy_repo.restore_vacancy(vacancy)
        for test_task in data_backup.test_tasks:
            await self.test_task_repo.restore_test_task(test_task)
        for candidate in data_backup.candidates:
            await self.candidate_repo.restore_candidate(candidate)
        for interview in data_backup.interviews:
            await self.interview_repo.restore_interview(interview)
        for offer in data_backup.offers:
            await self.offer_repo.restore_offer(offer)

    async def is_empty(self):
        return await self.admin_repo.is_empty()
