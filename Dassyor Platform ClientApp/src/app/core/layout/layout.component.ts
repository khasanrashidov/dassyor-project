import { Component } from '@angular/core';
import { AuthService } from '../../modules/auth/services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: false,
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class LayoutComponent {
  isAuthenticated = false;

  constructor(private readonly _authService: AuthService) {
    this.isAuthenticated = this._authService.isAuthenticated();
  }
}
