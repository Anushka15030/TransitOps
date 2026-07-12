"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/hooks/use-toast";
import type { MaintenanceFilters } from "@/types/maintenance";
import { maintenanceApi } from "../api/maintenance.api";
import type { CloseMaintenanceValues, OpenMaintenanceValues } from "../schemas/maintenance.schema";

const MAINTENANCE_KEY = "maintenance";

export function useMaintenanceRecords(filters: MaintenanceFilters) {
  return useQuery({
    queryKey: [MAINTENANCE_KEY, filters],
    queryFn: () => maintenanceApi.list(filters),
    placeholderData: (prev) => prev,
  });
}

export function useOpenMaintenance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: OpenMaintenanceValues) => maintenanceApi.open(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MAINTENANCE_KEY] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] }); // vehicle status changed too
      toast({ title: "Vehicle moved to In Shop" });
    },
    onError: (error: any) => {
      toast({
        title: "Cannot open maintenance",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useCloseMaintenance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CloseMaintenanceValues }) => maintenanceApi.close(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MAINTENANCE_KEY] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast({ title: "Maintenance closed — vehicle back in service" });
    },
    onError: (error: any) => {
      toast({
        title: "Cannot close maintenance",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}