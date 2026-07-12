"use client";

import { useState } from "react";
import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DataTable } from "@/components/shared/data-table";
import { DataTablePagination } from "@/components/shared/data-table-pagination";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { RequireRole } from "@/components/shared/require-role";

import { useCancelTrip, useCompleteTrip, useDeleteTrip, useDispatchTrip, useTrips } from "../hooks/useTrips";
import { getTripColumns } from "./trip-columns";
import { TripFormDialog } from "./trip-form-dialog";
import type { Trip, TripFilters } from "@/types/trip";

const PAGE_SIZE = 10;

export function TripTable() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [formOpen, setFormOpen] = useState(false);

  const [dispatchingTrip, setDispatchingTrip] = useState<Trip | null>(null);
  const [completingTrip, setCompletingTrip] = useState<Trip | null>(null);
  const [cancellingTrip, setCancellingTrip] = useState<Trip | null>(null);
  const [deletingTrip, setDeletingTrip] = useState<Trip | null>(null);

  const filters: TripFilters = {
    status: statusFilter === "all" ? undefined : (statusFilter as TripFilters["status"]),
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, isFetching } = useTrips(filters);
  const dispatchTrip = useDispatchTrip();
  const completeTrip = useCompleteTrip();
  const cancelTrip = useCancelTrip();
  const deleteTrip = useDeleteTrip();

  const columns = getTripColumns({
    onDispatch: setDispatchingTrip,
    onComplete: setCompletingTrip,
    onCancel: setCancellingTrip,
    onDelete: setDeletingTrip,
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="dispatched">Dispatched</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>

        <RequireRole allowed={["admin", "dispatcher"]}>
          <Button onClick={() => setFormOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Trip
          </Button>
        </RequireRole>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading || isFetching}
        emptyTitle="No trips found"
        emptyDescription="Create a draft trip to get started, or adjust your filters."
      />

      {data && data.total > 0 && (
        <DataTablePagination page={data.page} totalPages={data.total_pages} total={data.total} pageSize={data.page_size} onPageChange={setPage} />
      )}

      <TripFormDialog open={formOpen} onOpenChange={setFormOpen} />

      <ConfirmDialog
        open={!!dispatchingTrip}
        onOpenChange={(open) => !open && setDispatchingTrip(null)}
        title="Dispatch Trip"
        description={`Assign "${dispatchingTrip?.driver_name}" and "${dispatchingTrip?.vehicle_registration}" to this trip now? This locks both resources for the scheduled window.`}
        destructive={false}
        isLoading={dispatchTrip.isPending}
        onConfirm={() => dispatchingTrip && dispatchTrip.mutate(dispatchingTrip.id, { onSuccess: () => setDispatchingTrip(null) })}
      />

      <ConfirmDialog
        open={!!completingTrip}
        onOpenChange={(open) => !open && setCompletingTrip(null)}
        title="Mark Trip as Completed"
        description="This confirms the trip has finished and frees up the assigned driver."
        destructive={false}
        isLoading={completeTrip.isPending}
        onConfirm={() => completingTrip && completeTrip.mutate(completingTrip.id, { onSuccess: () => setCompletingTrip(null) })}
      />

      <ConfirmDialog
        open={!!cancellingTrip}
        onOpenChange={(open) => !open && setCancellingTrip(null)}
        title="Cancel Trip"
        description="This cancels the trip and releases the driver/vehicle assignment. This action cannot be undone."
        isLoading={cancelTrip.isPending}
        onConfirm={() => cancellingTrip && cancelTrip.mutate({ id: cancellingTrip.id }, { onSuccess: () => setCancellingTrip(null) })}
      />

      <ConfirmDialog
        open={!!deletingTrip}
        onOpenChange={(open) => !open && setDeletingTrip(null)}
        title="Delete Draft Trip"
        description="This permanently deletes the draft. It was never dispatched, so nothing operational is affected."
        isLoading={deleteTrip.isPending}
        onConfirm={() => deletingTrip && deleteTrip.mutate(deletingTrip.id, { onSuccess: () => setDeletingTrip(null) })}
      />
    </div>
  );
}