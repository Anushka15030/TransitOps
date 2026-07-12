"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "../api/auth.api";
import type { LoginFormValues } from "../schemas/auth.schema";

export function useLogin() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);

  return useMutation({
    mutationFn: (values: LoginFormValues) => authApi.login(values),
    onSuccess: (data) => {
      setSession(data.user, data.tokens.access_token);
      router.push("/dashboard");
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const clearSession = useAuthStore((s) => s.clearSession);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSettled: () => {
      clearSession();
      queryClient.clear();
      router.push("/login");
    },
  });
}

/**
 * On app load, the access token is empty (memory-only). This attempts a
 * silent refresh using the httpOnly cookie so a page reload doesn't force
 * a re-login if the user still has a valid session.
 */
export function useAuthInit() {
  const setSession = useAuthStore((s) => s.setSession);
  const setInitializing = useAuthStore((s) => s.setInitializing);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (user) {
      setInitializing(false);
      return;
    }
    (async () => {
      try {
        const tokens = await authApi.refresh();
        const me = await authApi.me();
        setSession(me, tokens.access_token);
      } catch {
        // No valid session — normal for a logged-out visitor, not an error to surface.
      } finally {
        setInitializing(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}