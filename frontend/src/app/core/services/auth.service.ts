import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    user_type: 'student' | 'employee' | 'admin';
    employee_id?: string;
    student_id?: string;
    phone_number?: string;
    department?: string;
    profile_image?: string;
    is_active: boolean;
    created_at: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access: string;
    refresh: string;
    user: User;
}

export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    user_type: string;
    department?: string;
    phone_number?: string;
}

@Injectable({
    providedIn: 'root'
})

export class AuthService {
    private apiUrl = environment.apiUrl + '/auth';
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    constructor(private http: HttpClient) {
        // Check if user is already logged in
        const token = this.getToken();
        if (token) {
            this.loadCurrentUser();
        }
    }

    login(credentials: LoginRequest): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, credentials)
            .pipe(
                tap(response => {
                    this.setTokens(response.access, response.refresh);
                    this.currentUserSubject.next(response.user);
                })
            );
    }

    register(userData: RegisterRequest): Observable<any> {
        return this.http.post(`${this.apiUrl}/register/`, userData);
    }

    logout(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.currentUserSubject.next(null);
    }

    refreshToken(): Observable<any> {
        const refreshToken = this.getRefreshToken();
        return this.http.post(`${this.apiUrl}/refresh/`, { refresh: refreshToken })
            .pipe(
                tap((response: any) => {
                    this.setTokens(response.access, refreshToken);
                })
            );
    }

    changePassword(data: { old_password: string, new_password: string, confirm_new_password: string }): Observable<any> {
        return this.http.put(`${this.apiUrl}/change-password/`, data);
    }

    requestPasswordReset(email: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/password-reset/`, { email });
    }

    confirmPasswordReset(data: { token: string, uid: string, new_password: string, confirm_new_password: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/password-reset/confirm/`, data);
    }

    private loadCurrentUser(): void {
        this.http.get<User>(`${this.apiUrl}/profile/`).subscribe({
            next: (user) => this.currentUserSubject.next(user),
            error: () => this.logout()
        });
    }

    private setTokens(accessToken: string, refreshToken: string): void {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    private getRefreshToken(): string | null {
        return localStorage.getItem('refresh_token');
    }

    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    getCurrentUser(): User | null {
        return this.currentUserSubject.value;
    }

    isAdmin(): boolean {
        const user = this.getCurrentUser();
        return user?.user_type === 'admin';
    }

    getAuthHeaders(): HttpHeaders {
        const token = this.getToken();
        return new HttpHeaders({
            'Authorization': `Bearer ${token}`
        });
    }
}