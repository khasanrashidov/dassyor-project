import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-email-verification',
  templateUrl: './email-verification.component.html',
  styleUrl: './email-verification.component.scss',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmailVerificationComponent {
  private readonly _router = inject(Router);

  navigateToLogin(): void {
    this._router.navigate(['/auth/login']);
  }
}
