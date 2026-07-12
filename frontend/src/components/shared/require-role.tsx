"use client";

import { useAuthStore } from "@/store/auth-store";

type Role = "admin" | "dispatcher" | "driver" | "customer";

/** Hides UI (buttons, nav items) the current role has no permission for. Backend still enforces the real check — this is UX polish, not a security boundary. */
export function RequireRole({ allowed, children }: { allowed: Role[]; children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  if (!user || !allowed.includes(user.role)) return null;
  return <>{children}</>;
}