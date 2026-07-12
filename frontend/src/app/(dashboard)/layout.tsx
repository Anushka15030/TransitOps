"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store/auth-store";
import { useAuthInit } from "@/features/auth/hooks/useAuth";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { LoadingSpinner } from "@/components/shared/loading-spinner";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  useAuthInit();
  const router = useRouter();
  const { user, isInitializing } = useAuthStore();

  useEffect(() => {
    if (!isInitializing && !user) {
      router.replace("/login");
    }
  }, [isInitializing, user, router]);

  if (isInitializing) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <LoadingSpinner label="Checking your session..." />
      </div>
    );
  }

  if (!user) return null; // redirect effect above is already firing

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar role={user.role} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar user={user} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}