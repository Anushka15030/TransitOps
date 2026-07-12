import { LoginForm } from "@/features/auth/components/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl border border-border bg-card p-8 shadow-xl">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Welcome to TransitOps
          </h1>
          <p className="text-sm text-muted-foreground">Sign in to manage your fleet operations</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}