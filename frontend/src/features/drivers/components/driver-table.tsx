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
import { useDeleteDriver, useDrivers } from "../hooks/useDrivers";
import { getDriverColumns } from "./driver-columns";
import { DriverFormDialog } from "./driver-form-dialog";
import type { Driver, DriverFilters } from "@/types/driver";

const PAGE_SIZE = 10;

export function DriverTable() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 400);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);

  const [formOpen, setFormOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [deletingDriver, setDeletingDriver] = useState<Driver | null>(null);

  const filters: DriverFilters = {
    search: debouncedSearch || undefined,
    status: statusFilter === "all" ? undefined : (statusFilter as DriverFilters["status"]),
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, isFetching } = useDrivers(filters);
  const deleteDriver = useDeleteDriver();

  const columns = getDriverColumns({
    onEdit: (driver) => {
      setEditingDriver(driver);
      setFormOpen(true);
    },
    onDelete: (driver) => setDeletingDriver(driver),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 flex-col gap-3 sm:flex-row">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search name, email, license..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-9"
            />
          </div>

          <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
            <SelectTrigger className="w-full sm:w-[160px]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="available">Available</SelectItem>
              <SelectItem value="on_trip">On Trip</SelectItem>
              <SelectItem value="off_duty">Off Duty</SelectItem>
              <SelectItem value="suspended">Suspended</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <RequireRole allowed={["admin", "dispatcher"]}>
          <Button
            onClick={() => {
              setEditingDriver(null);
              setFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Driver
          </Button>
        </RequireRole>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading || isFetching}
        emptyTitle="No drivers found"
        emptyDescription="Add your first driver to get started, or adjust your filters."
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

      <DriverFormDialog open={formOpen} onOpenChange={setFormOpen} driver={editingDriver} />

      <ConfirmDialog
        open={!!deletingDriver}
        onOpenChange={(open) => !open && setDeletingDriver(null)}
        title="Delete Driver"
        description={`Are you sure you want to remove "${deletingDriver?.full_name}" from active drivers? This action cannot be undone.`}
        isLoading={deleteDriver.isPending}
        onConfirm={() => {
          if (deletingDriver) {
            deleteDriver.mutate(deletingDriver.id, {
              onSuccess: () => setDeletingDriver(null),
            });
          }
        }}
      />
    </div>
  );
}