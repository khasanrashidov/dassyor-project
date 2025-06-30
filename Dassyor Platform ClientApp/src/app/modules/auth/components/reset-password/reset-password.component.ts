import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
  DestroyRef,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { MessageService } from 'primeng/api';

import { AuthService } from '../../services/auth.service';
import { ResetPasswordRequestModel } from '../../../../core/models/auth/reset-password-request.model';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResetPasswordComponent implements OnInit {
  private readonly _fb = inject(NonNullableFormBuilder);
  private readonly _authService = inject(AuthService);
  private readonly _router = inject(Router);
  private readonly _route = inject(ActivatedRoute);
  private readonly _messageService = inject(MessageService);
  private readonly _destroyRef = inject(DestroyRef);

  readonly isLoading = signal(false);
  readonly isResetSuccessful = signal(false);
  readonly invalidParams = signal(false);

  private _email: string | null = null;
  private _token: string | null = null;

  readonly resetPasswordForm = this._fb.group(
    {
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
    },
    {
      validators: this._passwordMatchValidator,
    }
  );

  ngOnInit(): void {
    this._getQueryParams();
  }

  onSubmit(): void {
    if (this.resetPasswordForm.invalid) {
      this.resetPasswordForm.markAllAsTouched();
      this._showErrorMessage('Please fill all fields correctly');
      return;
    }

    if (!this._email || !this._token) {
      this._showErrorMessage(
        'Invalid reset link. Please request a new password reset.'
      );
      return;
    }

    this.isLoading.set(true);
    const resetData: ResetPasswordRequestModel = {
      email: this._email,
      token: this._token,
      newPassword: this.resetPasswordForm.get('newPassword')?.value || '',
    };

    this._authService
      .resetPassword(resetData)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: result => {
          if (result.isSuccess) {
            this._showSuccessMessage(
              'Your password has been reset successfully'
            );
            this.isResetSuccessful.set(true);
          } else {
            this._showErrorMessage(
              result.message || 'Failed to reset password'
            );
          }
          this.isLoading.set(false);
        },
        error: error => {
          this._showErrorMessage('Reset failed: ' + error.message);
          this.isLoading.set(false);
        },
      });
  }

  navigateToLogin(): void {
    this._router.navigate(['/auth/login']);
  }

  private _passwordMatchValidator(
    control: AbstractControl
  ): ValidationErrors | null {
    const newPassword = control.get('newPassword');
    const confirmPassword = control.get('confirmPassword');

    if (
      newPassword &&
      confirmPassword &&
      newPassword.value !== confirmPassword.value
    ) {
      return { passwordMismatch: true };
    }

    return null;
  }

  private _getQueryParams(): void {
    this._route.queryParams.subscribe(params => {
      this._email = params['email'];
      this._token = params['token'];

      if (!this._email || !this._token) {
        this.invalidParams.set(true);
        this._showErrorMessage('Invalid or expired password reset link');
      }
    });
  }

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
