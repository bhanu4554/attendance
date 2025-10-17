import { Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth.guard';
import { AdminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'attendance',
    children: [
      {
        path: 'mark',
        loadComponent: () => import('./features/attendance/mark-attendance/mark-attendance.component').then(m => m.MarkAttendanceComponent),
        canActivate: [AuthGuard]
      },
      {
        path: 'records',
        loadComponent: () => import('./features/attendance/attendance-records/attendance-records.component').then(m => m.AttendanceRecordsComponent),
        canActivate: [AuthGuard]
      },
      {
        path: 'reports',
        loadComponent: () => import('./features/attendance/attendance-reports/attendance-reports.component').then(m => m.AttendanceReportsComponent),
        canActivate: [AuthGuard, AdminGuard]
      }
    ]
  },
  {
    path: 'users',
    children: [
      {
        path: 'profile',
        loadComponent: () => import('./features/users/profile/profile.component').then(m => m.ProfileComponent),
        canActivate: [AuthGuard]
      },
      {
        path: 'management',
        loadComponent: () => import('./features/users/user-management/user-management.component').then(m => m.UserManagementComponent),
        canActivate: [AuthGuard, AdminGuard]
      }
    ]
  },
  {
    path: 'face-recognition',
    children: [
      {
        path: 'register',
        loadComponent: () => import('./features/face-recognition/register-face/register-face.component').then(m => m.RegisterFaceComponent),
        canActivate: [AuthGuard]
      },
      {
        path: 'logs',
        loadComponent: () => import('./features/face-recognition/recognition-logs/recognition-logs.component').then(m => m.RecognitionLogsComponent),
        canActivate: [AuthGuard, AdminGuard]
      }
    ]
  },
  {
    path: '**',
    loadComponent: () => import('./shared/components/not-found/not-found.component').then(m => m.NotFoundComponent)
  }
];