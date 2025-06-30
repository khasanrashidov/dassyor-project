export interface ResetPasswordRequestModel {
  email: string;
  token: string;
  newPassword: string;
}
