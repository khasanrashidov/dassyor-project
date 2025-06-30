import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  OnDestroy,
  inject,
  signal,
  DestroyRef,
  AfterViewInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, Validators } from '@angular/forms';

import { MessageService } from 'primeng/api';

import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';

import { AuthService } from '../../services/auth.service';
import { LoginRequestModel } from '../../../../core/models/auth/login-request.model';
import { GoogleLoginRequestModel } from '../../../../core/models/auth/google-login-request.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent implements OnInit, OnDestroy, AfterViewInit {
  private readonly _fb = inject(NonNullableFormBuilder);
  private readonly _authService = inject(AuthService);
  private readonly _messageService = inject(MessageService);
  private readonly _socialAuthService = inject(SocialAuthService);
  private readonly _router = inject(Router);
  private readonly _destroyRef = inject(DestroyRef);

  readonly isLoading = signal(false);
  readonly isGoogleSignInLoading = signal(false);
  readonly isMobileView = signal(window.innerWidth < 768);

  readonly loginForm = this._fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  googleButtonVisible = true;

  ngOnInit(): void {
    this._setupResponsiveListener();
    this._setupGoogleAuth();
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.googleButtonVisible = false;
      setTimeout(() => (this.googleButtonVisible = true), 0);
    }, 0);
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this._onWindowResize);
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this._showErrorMessage('Please fill all required fields correctly');
      return;
    }

    this.isLoading.set(true);
    const loginData: LoginRequestModel = this.loginForm.getRawValue();

    this._authService
      .login(loginData)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: result => {
          if (result.isSuccess) {
            // this._showSuccessMessage('Login successful');
          } else {
            this._showErrorMessage(result.message || 'Login failed');
          }
          this.isLoading.set(false);
        },
        error: error => {
          this._showErrorMessage('Login failed: ' + error.message);
          this.isLoading.set(false);
        },
      });
  }

  navigateToRegister(): void {
    this._router.navigate(['/auth/register']);
  }

  navigateToForgotPassword(): void {
    this._router.navigate(['/auth/forgot-password']);
  }

  private _processGoogleLogin(user: SocialUser): void {
    this.isGoogleSignInLoading.set(true);

    const googleData: GoogleLoginRequestModel = {
      credential: user.idToken,
    };

    this._authService
      .googleLogin(googleData)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: result => {
          if (result.isSuccess) {
            // this._showSuccessMessage('Google login successful');
          } else {
            this._showErrorMessage(result.message || 'Google login failed');
          }
          this.isGoogleSignInLoading.set(false);
        },
        error: error => {
          this._showErrorMessage('Google login failed: ' + error.message);
          this.isGoogleSignInLoading.set(false);
        },
      });
  }

  private _setupResponsiveListener(): void {
    window.addEventListener('resize', this._onWindowResize);
  }

  private _setupGoogleAuth(): void {
    this._socialAuthService.authState
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe(user => {
        if (user) {
          this._processGoogleLogin(user);
        }
      });
  }

  private _onWindowResize = (): void => {
    this.isMobileView.set(window.innerWidth < 768);
  };

  private _showSuccessMessage(detail: string): void {
    this._messageService.add({
      severity: 'success',
      summary: 'Success',
      detail,
    });
  }

  private _showErrorMessage(detail: string): void {
    this._messageService.add({
      severity: 'error',
      summary: 'Error',
      detail,
    });
  }
}
