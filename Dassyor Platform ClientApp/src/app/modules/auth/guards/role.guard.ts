import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
} from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root',
})
export class RoleGuard implements CanActivate {
  constructor(
    private readonly _authService: AuthService,
    private readonly _router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    // First check if the user is authenticated
    if (!this._authService.isAuthenticated()) {
      this._router.navigate(['/auth']);
      return false;
    }

    // Check if route has data for required roles
    const requiredRoles = route.data['roles'] as string[];

    if (!requiredRoles || requiredRoles.length === 0) {
      return true; // No specific roles required
    }

    // Check if user has any of the required roles
    const hasRequiredRole = requiredRoles.some(role =>
      this._authService.hasRole(role)
    );

    if (!hasRequiredRole) {
      // Redirect to a forbidden/unauthorized page or dashboard
      this._router.navigate(['/error/forbidden']);
      return false;
    }

    return true;
  }
}

// Sample usage in a route
// {
//   path: 'admin',
//   component: AdminComponent,
//   canActivate: [RoleGuard],
//   data: { roles: ['ADMIN'] }
// }
