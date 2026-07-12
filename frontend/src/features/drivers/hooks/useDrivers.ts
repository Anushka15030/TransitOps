"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/hooks/use-toast";
import type { DriverFilters } from "@/types/driver";
import { driverApi } from "../api/driver.api";
import type { DriverCreateValues, DriverUpdateValues } from "../schemas/driver.schema";

const DRIVERS_KEY = "drivers";

export function useDrivers(filters: DriverFilters) {
  return useQuery({
    queryKey: [DRIVERS_KEY, filters],
    queryFn: () => driverApi.list(filters),
    placeholderData: (previousData) => previousData,
  });
}

export function useCreateDriver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DriverCreateValues) => driverApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DRIVERS_KEY] });
      toast({ title: "Driver added successfully" });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to add driver",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useUpdateDriver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: DriverUpdateValues }) =>
      driverApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DRIVERS_KEY] });
      toast({ title: "Driver updated successfully" });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to update driver",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useDeleteDriver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => driverApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DRIVERS_KEY] });
      toast({ title: "Driver deleted" });
    },
    onError: (error: any) => {
      toast({
        title: "Cannot delete driver",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}