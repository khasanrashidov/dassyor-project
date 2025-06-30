export interface AuthResultModel {
  tokenType: string;
  accessToken: string;
  expiration: Date;
  userId: string;
  roles: string[];
  expiresInSeconds: number;
  message: string;
  isSuccess: boolean;
  errors: string[];
}
