/**
 * Access token lives ONLY in memory (Zustand, no persist middleware).
 * This is a deliberate XSS mitigation: if the token were in localStorage,
 * any injected script could read it directly. Keeping it in memory means
 * a page refresh loses it — which is fine, because we silently re-fetch
 * a new one via the httpOnly refresh cookie on app load (see useAuth).
 */
import { create } from "zustand";
import type { AuthUser } from "@/types/api";

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isInitializing: boolean; // true until the first silent-refresh attempt completes
  setSession: (user: AuthUser, accessToken: string) => void;
  clearSession: () => void;
  setInitializing: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isInitializing: true,
  setSession: (user, accessToken) => set({ user, accessToken }),
  clearSession: () => set({ user: null, accessToken: null }),
  setInitializing: (value) => set({ isInitializing: value }),
}));