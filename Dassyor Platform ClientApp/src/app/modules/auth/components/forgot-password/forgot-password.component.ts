import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
  DestroyRef,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { MessageService } from 'primeng/api';

import { AuthService } from '../../services/auth.service';
import { ForgotPasswordRequestModel } from '../../../../core/models/auth/forgot-password-request.model';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ForgotPasswordComponent {
  private readonly _fb = inject(NonNullableFormBuilder);
  private readonly _authService = inject(AuthService);
  private readonly _router = inject(Router);
  private readonly _messageService = inject(MessageService);
  private readonly _destroyRef = inject(DestroyRef);

  readonly isLoading = signal(false);
  readonly isSubmitted = signal(false);

  readonly forgotPasswordForm = this._fb.group({
    email: ['', [Validators.required, Validators.email]],
  });

  navigateToLogin(): void {
    this._router.navigate(['/auth/login']);
  }

  onSubmit(): void {
    if (this.forgotPasswordForm.invalid) {
      this.forgotPasswordForm.markAllAsTouched();
      this._showErrorMessage('Please enter a valid email address');
      return;
    }

    this.isLoading.set(true);
    const resetData: ForgotPasswordRequestModel =
      this.forgotPasswordForm.getRawValue();

    this._authService
      .forgotPassword(resetData)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: result => {
          if (result.isSuccess) {
            this._showSuccessMessage(
              'Password reset link has been sent to your email'
            );
            this.isSubmitted.set(true);
          } else {
            this._showErrorMessage(
              result.message || 'Failed to process request'
            );
          }
          this.isLoading.set(false);
        },
        error: error => {
          this._showErrorMessage('Request failed: ' + error.message);
          this.isLoading.set(false);
        },
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
