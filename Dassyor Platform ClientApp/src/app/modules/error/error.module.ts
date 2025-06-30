import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorForbiddenComponent } from './components/error-forbidden/error-forbidden.component';
import { ErrorNotFoundComponent } from './components/error-not-found/error-not-found.component';
import { ErrorRoutingModule } from './error-routing.module';

@NgModule({
  declarations: [ErrorForbiddenComponent, ErrorNotFoundComponent],
  imports: [CommonModule, ErrorRoutingModule],
})
export class ErrorModule {}
