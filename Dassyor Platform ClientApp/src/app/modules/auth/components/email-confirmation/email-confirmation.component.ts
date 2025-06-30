import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
  DestroyRef,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';

import { MessageService } from 'primeng/api';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-email-confirmation',
  templateUrl: './email-confirmation.component.html',
  styleUrl: './email-confirmation.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmailConfirmationComponent implements OnInit {
  private readonly _authService = inject(AuthService);
  private readonly _router = inject(Router);
  private readonly _route = inject(ActivatedRoute);
  private readonly _messageService = inject(MessageService);
  private readonly _destroyRef = inject(DestroyRef);

  readonly isLoading = signal(true);
  readonly confirmationStatus = signal<'pending' | 'success' | 'error'>(
    'pending'
  );

  ngOnInit(): void {
    this._processConfirmation();
  }

  navigateToLogin(): void {
    this._router.navigate(['/auth/login']);
  }

  private _processConfirmation(): void {
    const userId = this._route.snapshot.queryParamMap.get('userid');
    const token = this._route.snapshot.queryParamMap.get('token');

    if (!userId || !token) {
      this.isLoading.set(false);
      this.confirmationStatus.set('error');
      this._showErrorMessage('Invalid confirmation link');
      return;
    }

    this._authService
      .confirmEmail(userId, token)
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe({
        next: () => {
          this.isLoading.set(false);
          this.confirmationStatus.set('success');
          this._showSuccessMessage(
            'Your email has been confirmed successfully'
          );
        },
        error: error => {
          this.isLoading.set(false);
          this.confirmationStatus.set('error');
          this._showErrorMessage('Confirmation failed: ' + error.message);
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
