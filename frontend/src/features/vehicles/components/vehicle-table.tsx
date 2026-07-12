"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DataTable } from "@/components/shared/data-table";
import { DataTablePagination } from "@/components/shared/data-table-pagination";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { RequireRole } from "@/components/shared/require-role";

import { useDebounce } from "@/hooks/use-debounce";
import { useDeleteVehicle, useVehicles } from "../hooks/useVehicles";
import { getVehicleColumns } from "./vehicle-columns";
import { VehicleFormDialog } from "./vehicle-form-dialog";
import type { Vehicle, VehicleFilters } from "@/types/vehicle";

const PAGE_SIZE = 10;

export function VehicleTable() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 400);
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);

  const [formOpen, setFormOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [deletingVehicle, setDeletingVehicle] = useState<Vehicle | null>(null);

  const filters: VehicleFilters = {
    search: debouncedSearch || undefined,
    vehicle_type: typeFilter === "all" ? undefined : (typeFilter as VehicleFilters["vehicle_type"]),
    status: statusFilter === "all" ? undefined : (statusFilter as VehicleFilters["status"]),
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, isFetching } = useVehicles(filters);
  const deleteVehicle = useDeleteVehicle();

  const columns = getVehicleColumns({
    onEdit: (vehicle) => {
      setEditingVehicle(vehicle);
      setFormOpen(true);
    },
    onDelete: (vehicle) => setDeletingVehicle(vehicle),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 flex-col gap-3 sm:flex-row">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search registration, make, model..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-9"
            />
          </div>

          <Select value={typeFilter} onValueChange={(v) => { setTypeFilter(v); setPage(1); }}>
            <SelectTrigger className="w-full sm:w-[160px]">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="bus">Bus</SelectItem>
              <SelectItem value="mini_bus">Mini Bus</SelectItem>
              <SelectItem value="van">Van</SelectItem>
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
            <SelectTrigger className="w-full sm:w-[160px]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="maintenance">Maintenance</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <RequireRole allowed={["admin", "dispatcher"]}>
          <Button
            onClick={() => {
              setEditingVehicle(null);
              setFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Vehicle
          </Button>
        </RequireRole>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading || isFetching}
        emptyTitle="No vehicles found"
        emptyDescription="Add your first vehicle to get started, or adjust your filters."
      />

      {data && data.total > 0 && (
        <DataTablePagination
          page={data.page}
          totalPages={data.total_pages}
          total={data.total}
          pageSize={data.page_size}
          onPageChange={setPage}
        />
      )}

      <VehicleFormDialog open={formOpen} onOpenChange={setFormOpen} vehicle={editingVehicle} />

      <ConfirmDialog
        open={!!deletingVehicle}
        onOpenChange={(open) => !open && setDeletingVehicle(null)}
        title="Delete Vehicle"
        description={`Are you sure you want to delete "${deletingVehicle?.registration_number}"? This action cannot be undone.`}
        isLoading={deleteVehicle.isPending}
        onConfirm={() => {
          if (deletingVehicle) {
            deleteVehicle.mutate(deletingVehicle.id, {
              onSuccess: () => setDeletingVehicle(null),
            });
          }
        }}
      />
    </div>
  );
}