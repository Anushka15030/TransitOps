"use client";

import { useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { Plus, Wrench } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DataTable } from "@/components/shared/data-table";
import { DataTablePagination } from "@/components/shared/data-table-pagination";
import { StatusBadge } from "@/components/shared/status-badge";
import { RequireRole } from "@/components/shared/require-role";

import { useMaintenanceRecords } from "../hooks/useMaintenance";
import { OpenMaintenanceDialog } from "./open-maintenance-dialog";
import { CloseMaintenanceDialog } from "./close-maintenance-dialog";
import type { MaintenanceFilters, MaintenanceRecord } from "@/types/maintenance";

const PAGE_SIZE = 10;

export function MaintenanceTable() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [openDialogOpen, setOpenDialogOpen] = useState(false);
  const [closingRecord, setClosingRecord] = useState<MaintenanceRecord | null>(null);

  const filters: MaintenanceFilters = {
    status: statusFilter === "all" ? undefined : (statusFilter as MaintenanceFilters["status"]),
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, isFetching } = useMaintenanceRecords(filters);

  const columns: ColumnDef<MaintenanceRecord>[] = [
    {
      id: "vehicle",
      header: "Vehicle",
      cell: ({ row }) => <span className="font-mono font-medium text-foreground">{row.original.vehicle_registration}</span>,
    },
    {
      accessorKey: "reported_issue",
      header: "Issue",
      cell: ({ row }) => <span className="line-clamp-1 max-w-xs">{row.original.reported_issue}</span>,
    },
    {
      accessorKey: "opened_at",
      header: "Opened",
      cell: ({ row }) => new Date(row.original.opened_at).toLocaleDateString(),
    },
    {
      accessorKey: "estimated_cost",
      header: "Est. Cost",
      cell: ({ row }) => (row.original.estimated_cost != null ? `₹${row.original.estimated_cost.toFixed(2)}` : "—"),
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) =>
        row.original.status === "open" ? (
          <Button variant="outline" size="sm" onClick={() => setClosingRecord(row.original)}>
            <Wrench className="mr-2 h-3.5 w-3.5" />
            Close
          </Button>
        ) : null,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
          <SelectTrigger className="w-full sm:w-[160px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>

        <RequireRole allowed={["admin", "dispatcher"]}>
          <Button onClick={() => setOpenDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Log Maintenance
          </Button>
        </RequireRole>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading || isFetching}
        emptyTitle="No maintenance records"
        emptyDescription="All vehicles are in service. Log an issue to begin tracking maintenance."
      />

      {data && data.total > 0 && (
        <DataTablePagination page={data.page} totalPages={data.total_pages} total={data.total} pageSize={data.page_size} onPageChange={setPage} />
      )}

      <OpenMaintenanceDialog open={openDialogOpen} onOpenChange={setOpenDialogOpen} />
      <CloseMaintenanceDialog record={closingRecord} onOpenChange={(open) => !open && setClosingRecord(null)} />
    </div>
  );
}