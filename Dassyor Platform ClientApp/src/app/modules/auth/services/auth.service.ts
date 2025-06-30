import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { catchError, Observable, throwError } from 'rxjs';
import { tap } from 'rxjs/operators';

import { environment } from '../../../../environments/environment';
import { AuthResultModel } from '../../../core/models/auth/auth-result.model';
import { LoginRequestModel } from '../../../core/models/auth/login-request.model';
import { RegisterRequestModel } from '../../../core/models/auth/register-request.model';
import { GoogleLoginRequestModel } from '../../../core/models/auth/google-login-request.model';
import { ForgotPasswordRequestModel } from '../../../core/models/auth/forgot-password-request.model';
import { ResetPasswordRequestModel } from '../../../core/models/auth/reset-password-request.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly BASE_AUTH_API_URL = `${environment.apiUrl}/api/auth`;

  private readonly _router = inject(Router);
  private readonly _http = inject(HttpClient);

  login(data: LoginRequestModel): Observable<AuthResultModel> {
    return this._http
      .post<AuthResultModel>(`${this.BASE_AUTH_API_URL}/login`, data)
      .pipe(
        tap(result => {
          this.storeAuthData(result);
          if (result.isSuccess) {
            this.handleSuccessfulLogin();
          }
        }),
        catchError(error => {
          return throwError(
            () => new Error(error.error.message || 'Login failed')
          );
        })
      );
  }

  register(data: RegisterRequestModel): Observable<AuthResultModel> {
    return this._http
      .post<AuthResultModel>(`${this.BASE_AUTH_API_URL}/register`, data)
      .pipe(
        tap(result => {
          if (result.isSuccess) {
            this._router.navigate(['/auth/email-verification']);
          }
        }),
        catchError(error => {
          return throwError(
            () => new Error(error.error.message || 'Registration failed')
          );
        })
      );
  }

  googleLogin(data: GoogleLoginRequestModel): Observable<AuthResultModel> {
    return this._http
      .post<AuthResultModel>(`${this.BASE_AUTH_API_URL}/google-login`, data)
      .pipe(
        tap(result => {
          this.storeAuthData(result);
          if (result.isSuccess) {
            this.handleSuccessfulLogin();
          }
        })
      );
  }

  forgotPassword(
    data: ForgotPasswordRequestModel
  ): Observable<AuthResultModel> {
    return this._http.post<AuthResultModel>(
      `${this.BASE_AUTH_API_URL}/forgot-password`,
      data
    );
  }

  resetPassword(data: ResetPasswordRequestModel): Observable<AuthResultModel> {
    return this._http
      .post<AuthResultModel>(`${this.BASE_AUTH_API_URL}/reset-password`, data)
      .pipe(
        catchError(error => {
          return throwError(
            () => new Error(error.error.message || 'Password reset failed')
          );
        })
      );
  }

  confirmEmail(userId: string, token: string): Observable<AuthResultModel> {
    return this._http
      .get<AuthResultModel>(`${this.BASE_AUTH_API_URL}/confirm-email`, {
        params: { userId, token },
      })
      .pipe(
        catchError(error => {
          return throwError(
            () => new Error(error.error.message || 'Email confirmation failed')
          );
        })
      );
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    this._router.navigate(['/auth']);
    window.location.reload();
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return false;
    }

    // Check token expiration
    try {
      const userData = JSON.parse(localStorage.getItem('auth_user') || '{}');
      const expiration = userData.expiration;
      if (expiration && new Date(expiration) < new Date()) {
        this.logout();
        return false;
      }
      return true;
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      return !!token;
    }
  }

  private handleSuccessfulLogin(): void {
    // Check if there's a stored redirect URL
    const redirectUrl = sessionStorage.getItem('redirectUrl') || '/dashboard';
    sessionStorage.removeItem('redirectUrl');
    window.location.href = redirectUrl;
  }

  private storeAuthData(result: AuthResultModel): void {
    if (result.isSuccess && result.accessToken) {
      localStorage.setItem('auth_token', result.accessToken);
      localStorage.setItem(
        'auth_user',
        JSON.stringify({
          userId: result.userId,
          roles: result.roles,
          expiration: result.expiration,
        })
      );
    }
  }

  getUserRoles(): string[] {
    try {
      const userData = JSON.parse(localStorage.getItem('auth_user') || '{}');
      return userData.roles || [];
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      return [];
    }
  }

  hasRole(role: string): boolean {
    const roles = this.getUserRoles();
    return roles.includes(role);
  }
}
