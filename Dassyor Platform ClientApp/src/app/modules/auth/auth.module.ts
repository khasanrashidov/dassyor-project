import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthRoutingModule } from './auth-routing.module';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { ForgotPasswordComponent } from './components/forgot-password/forgot-password.component';
import { Toast } from 'primeng/toast';
import { Divider } from 'primeng/divider';
import { Password } from 'primeng/password';
import { ReactiveFormsModule } from '@angular/forms';
import { Card } from 'primeng/card';
import { Button } from 'primeng/button';
import { MessageService } from 'primeng/api';
import { InputTextModule } from 'primeng/inputtext';
import { FloatLabelModule } from 'primeng/floatlabel';
import { GoogleSigninButtonModule } from '@abacritt/angularx-social-login';
import { CheckboxModule } from 'primeng/checkbox';
import { AutoFocusModule } from 'primeng/autofocus';
import { EmailVerificationComponent } from './components/email-verification/email-verification.component';
import { ResetPasswordComponent } from './components/reset-password/reset-password.component';
import { EmailConfirmationComponent } from './components/email-confirmation/email-confirmation.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';

@NgModule({
  declarations: [
    LoginComponent,
    RegisterComponent,
    ForgotPasswordComponent,
    EmailVerificationComponent,
    ResetPasswordComponent,
    EmailConfirmationComponent,
  ],
  imports: [
    CommonModule,
    AuthRoutingModule,
    ReactiveFormsModule,
    Card,
    InputTextModule,
    Password,
    Toast,
    Divider,
    Button,
    FloatLabelModule,
    GoogleSigninButtonModule,
    CheckboxModule,
    AutoFocusModule,
    ProgressSpinnerModule,
  ],
  providers: [MessageService],
})
export class AuthModule {}
