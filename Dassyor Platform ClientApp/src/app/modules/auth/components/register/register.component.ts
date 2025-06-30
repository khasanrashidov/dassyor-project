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
import {
  NonNullableFormBuilder,
  Validators,
  AbstractControl,
  ValidationErrors,
} from '@angular/forms';

import { MessageService } from 'primeng/api';

import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';

import { AuthService } from '../../services/auth.service';
import { RegisterRequestModel } from '../../../../core/models/auth/register-request.model';
import { GoogleLoginRequestModel } from '../../../../core/models/auth/google-login-request.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegisterComponent implements OnInit, OnDestroy, AfterViewInit {
  private readonly _fb = inject(NonNullableFormBuilder);
  private readonly _router = inject(Router);
  private readonly _authService = inject(AuthService);
  private readonly _messageService = inject(MessageService);
  private readonly _socialAuthService = inject(SocialAuthService);
  private readonly _destroyRef = inject(DestroyRef);

  readonly isLoading = signal(false);
  readonly isGoogleSignInLoading = signal(false);
  readonly isMobileView = signal(window.innerWidth < 768);

  readonly PRIVACY_POLICY_LINK = 'https://dassyor.com/privacy';
  readonly TERMS_OF_SERVICE_LINK = 'https://dassyor.com/terms';

  readonly registerForm = this._fb.group(
    {
      email: [
        '',
        [Validators.required, Validators.email, Validators.maxLength(254)],
      ],
      password: [
        '',
        [
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(128),
        ],
      ],
      confirmPassword: ['', [Validators.required]],
      acceptTerms: [false, [Validators.requiredTrue]],
    },
    { validators: this._passwordMatchValidator }
  );

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
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();

      if (
        !this.registerForm.get('email')?.valid ||
        !this.registerForm.get('password')?.valid
      ) {
        this._showErrorMessage('Please fill all required fields correctly');
      } else if (this.registerForm.hasError('passwordMismatch')) {
        this._showErrorMessage('Passwords do not match');
      } else if (!this.registerForm.get('acceptTerms')?.value) {
        this._showErrorMessage(
          'You must accept the Terms of Service and Privacy Policy'
        );
      }
      return;
    }

    this.isLoading.set(true);
    const formValue = this.registerForm.getRawValue();

    const registerData: RegisterRequestModel = {
      email: formValue.email,
      password: formValue.password,
    };

    this._authService
      .register(registerData)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: result => {
          if (result.isSuccess) {
            // this._showSuccessMessage(
            //   'Registration successful! Please check your email to verify your account.'
            // );
          } else {
            this._showErrorMessage(result.message || 'Registration failed');
          }
          this.isLoading.set(false);
        },
        error: error => {
          this._showErrorMessage('Registration failed: ' + error.message);
          this.isLoading.set(false);
        },
      });
  }

  navigateToLogin(): void {
    this._router.navigate(['/auth/login']);
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
            // this._showSuccessMessage('Google registration successful');
          } else {
            this._showErrorMessage(
              result.message || 'Google registration failed'
            );
          }
          this.isGoogleSignInLoading.set(false);
        },
        error: error => {
          this._showErrorMessage(
            'Google registration failed: ' + error.message
          );
          this.isGoogleSignInLoading.set(false);
        },
      });
  }

  private _passwordMatchValidator(
    control: AbstractControl
  ): ValidationErrors | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');

    if (
      password &&
      confirmPassword &&
      password.value !== confirmPassword.value
    ) {
      return { passwordMismatch: true };
    }

    return null;
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
