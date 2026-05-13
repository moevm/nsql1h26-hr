// hooks/usePermissions.ts
import { useMemo } from 'react';

export type UserRole = 'ADMIN' | 'HR' | 'MANAGER' | 'TECH_SPEC';

interface Permissions {
  // Вакансии
  canViewVacancies: boolean;
  canCreateVacancy: boolean;
  canEditVacancy: boolean;
  canDeleteVacancy: boolean;
  
  // Кандидаты
  canViewCandidates: boolean;
  canCreateCandidate: boolean;
  canEditCandidate: boolean;
  canDeleteCandidate: boolean;
  
  // Тестовые задания
  canViewTestTasks: boolean;
  canCreateTestTask: boolean;
  canEditTestTask: boolean;
  canDeleteTestTask: boolean;
  
  // Интервью
  canViewInterviews: boolean;
  canCreateInterview: boolean;
  canEditInterview: boolean;      // только для TECH_SPEC (оставить отзыв)
  canDeleteInterview: boolean;
  
  // Офферы
  canViewOffers: boolean;
  canCreateOffer: boolean;
  canEditOfferStatus: boolean;     // согласование оффера (MANAGER)
  canDeleteOffer: boolean;
  
  // Пользователи (только ADMIN)
  canViewUsers: boolean;
  canCreateUser: boolean;
  canEditUser: boolean;
  canDeleteUser: boolean;
}

export function usePermissions(userRole: UserRole | null | undefined): Permissions {
  return useMemo(() => {
    // Если пользователь не авторизован
    if (!userRole) {
      return {
        canViewVacancies: false,
        canCreateVacancy: false,
        canEditVacancy: false,
        canDeleteVacancy: false,
        canViewCandidates: false,
        canCreateCandidate: false,
        canEditCandidate: false,
        canDeleteCandidate: false,
        canViewTestTasks: false,
        canCreateTestTask: false,
        canEditTestTask: false,
        canDeleteTestTask: false,
        canViewInterviews: false,
        canCreateInterview: false,
        canEditInterview: false,
        canDeleteInterview: false,
        canViewOffers: false,
        canCreateOffer: false,
        canEditOfferStatus: false,
        canDeleteOffer: false,
        canViewUsers: false,
        canCreateUser: false,
        canEditUser: false,
        canDeleteUser: false,
      };
    }

    // Базовые права для всех авторизованных пользователей
    const basePermissions = {
      // Просмотр доступен всем
      canViewVacancies: true,
      canViewCandidates: true,
      canViewTestTasks: true,
      canViewInterviews: true,
      canViewOffers: true,
    };

    // Права для ADMIN
    if (userRole === 'ADMIN') {
      return {
        ...basePermissions,
        canCreateVacancy: true,
        canEditVacancy: true,
        canDeleteVacancy: true,
        canCreateCandidate: true,
        canEditCandidate: true,
        canDeleteCandidate: true,
        canCreateTestTask: true,
        canEditTestTask: true,
        canDeleteTestTask: true,
        canCreateInterview: true,
        canEditInterview: true,
        canDeleteInterview: true,
        canCreateOffer: true,
        canEditOfferStatus: true,
        canDeleteOffer: true,
        canViewUsers: true,
        canCreateUser: true,
        canEditUser: true,
        canDeleteUser: true,
      };
    }

    // Права для HR
    if (userRole === 'HR') {
      return {
        ...basePermissions,
        canCreateVacancy: true,
        canEditVacancy: true,
        canDeleteVacancy: true,
        canCreateCandidate: true,
        canEditCandidate: true,
        canDeleteCandidate: true,
        canCreateTestTask: true,
        canEditTestTask: true,
        canDeleteTestTask: true,
        canCreateInterview: true,
        canEditInterview: false,      // HR не может редактировать интервью
        canDeleteInterview: true,
        canCreateOffer: true,
        canEditOfferStatus: false,    // HR не может согласовывать офферы
        canDeleteOffer: true,
        canViewUsers: false,
        canCreateUser: false,
        canEditUser: false,
        canDeleteUser: false,
      };
    }

    // Права для MANAGER
    if (userRole === 'MANAGER') {
      return {
        ...basePermissions,
        canViewVacancies: false,
        canViewTestTasks: false,
        canCreateVacancy: false,
        canEditVacancy: false,
        canDeleteVacancy: false,
        canCreateCandidate: false,
        canEditCandidate: false,
        canDeleteCandidate: false,
        canCreateTestTask: false,
        canEditTestTask: false,
        canDeleteTestTask: false,
        canCreateInterview: false,
        canEditInterview: false,
        canDeleteInterview: false,
        canCreateOffer: true,          // Менеджер может создавать офферы
        canEditOfferStatus: true,      // Менеджер может согласовывать офферы
        canDeleteOffer: false,
        canViewUsers: false,
        canCreateUser: false,
        canEditUser: false,
        canDeleteUser: false,
      };
    }

    // Права для TECH_SPEC
    if (userRole === 'TECH_SPEC') {
      return {
        ...basePermissions,
        canViewVacancies: false,
        canViewOffers: false,
        canCreateVacancy: false,
        canEditVacancy: false,
        canDeleteVacancy: false,
        canCreateCandidate: false,
        canEditCandidate: false,
        canDeleteCandidate: false,
        canCreateTestTask: false,
        canEditTestTask: false,
        canDeleteTestTask: false,
        canCreateInterview: false,
        canEditInterview: true,         // Техспец может оставлять отзыв
        canDeleteInterview: false,
        canCreateOffer: false,
        canEditOfferStatus: false,
        canDeleteOffer: false,
        canViewUsers: false,
        canCreateUser: false,
        canEditUser: false,
        canDeleteUser: false,
      };
    }

    // Fallback
    return basePermissions as Permissions;
  }, [userRole]);
}
