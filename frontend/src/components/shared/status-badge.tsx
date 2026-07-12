import { cn } from "@/lib/utils";

type StatusVariant = "success" | "warning" | "danger" | "neutral" | "info";

const STATUS_CONFIG: Record<string, { label: string; variant: StatusVariant }> = {
  active: { label: "Active", variant: "success" },
  maintenance: { label: "Maintenance", variant: "warning" },
  inactive: { label: "Inactive", variant: "neutral" },
  available: { label: "Available", variant: "success" },
  on_trip: { label: "On Trip", variant: "info" },
  off_duty: { label: "Off Duty", variant: "neutral" },
  suspended: { label: "Suspended", variant: "danger" },
  scheduled: { label: "Scheduled", variant: "info" },
  ongoing: { label: "Ongoing", variant: "warning" },
  completed: { label: "Completed", variant: "success" },
  cancelled: { label: "Cancelled", variant: "danger" },
  pending: { label: "Pending", variant: "warning" },
  confirmed: { label: "Confirmed", variant: "success" },
};

const VARIANT_STYLES: Record<StatusVariant, string> = {
  success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  danger: "bg-red-500/10 text-red-400 border-red-500/20",
  neutral: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? { label: status, variant: "neutral" as StatusVariant };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        VARIANT_STYLES[config.variant]
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {config.label}
    </span>
  );
}