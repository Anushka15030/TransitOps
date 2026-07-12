import { apiClient } from "@/lib/api-client";
import type { LoginResponse } from "@/types/api";
import type { LoginFormValues, RegisterFormValues } from "../schemas/auth.schema";

export const authApi = {
  login: (payload: LoginFormValues) =>
    apiClient.post<LoginResponse>("/auth/login", payload).then((res) => res.data),

  register: (payload: Omit<RegisterFormValues, "confirmPassword">) =>
    apiClient.post("/auth/register", payload).then((res) => res.data),

  refresh: () => apiClient.post("/auth/refresh").then((res) => res.data),

  logout: () => apiClient.post("/auth/logout"),

  me: () => apiClient.get("/auth/me").then((res) => res.data),
};