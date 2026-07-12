export interface ApiError {
  success: false;
  error: { message: string };
}

export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  role: "admin" | "dispatcher" | "driver" | "customer";
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  user: AuthUser;
  tokens: TokenResponse;
}