import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
  CanActivateChild,
  CanLoad,
  Route,
  UrlSegment,
} from '@angular/router';
import { Observable } from 'rxjs';

import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate, CanActivateChild, CanLoad {
  constructor(
    private readonly _authService: AuthService,
    private readonly _router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.checkAuth(state.url);
  }

  canActivateChild(
    childRoute: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.canActivate(childRoute, state);
  }

  canLoad(
    route: Route,
    segments: UrlSegment[]
  ): Observable<boolean> | Promise<boolean> | boolean {
    const url = segments.map(s => `/${s.path}`).join('');
    return this.checkAuth(url);
  }

  private checkAuth(url: string): boolean {
    if (this._authService.isAuthenticated()) {
      return true;
    }

    // Store the attempted URL for redirecting after login
    this.storeRedirectUrl(url);

    // Navigate to the login page
    this._router.navigate(['/auth']);

    return false;
  }

  private storeRedirectUrl(url: string): void {
    // Don't redirect to the auth page itself
    if (url && !url.startsWith('/auth')) {
      sessionStorage.setItem('redirectUrl', url);
    }
  }
}
