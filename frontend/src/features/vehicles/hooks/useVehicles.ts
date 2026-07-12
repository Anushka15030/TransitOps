"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/hooks/use-toast";
import type { VehicleFilters } from "@/types/vehicle";
import { vehicleApi } from "../api/vehicle.api";
import type { VehicleFormValues } from "../schemas/vehicle.schema";

const VEHICLES_KEY = "vehicles";

export function useVehicles(filters: VehicleFilters) {
  return useQuery({
    queryKey: [VEHICLES_KEY, filters],
    queryFn: () => vehicleApi.list(filters),
    placeholderData: (previousData) => previousData, // keeps old page visible while next page loads
  });
}

export function useCreateVehicle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: VehicleFormValues) => vehicleApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VEHICLES_KEY] });
      toast({ title: "Vehicle added successfully" });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to add vehicle",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useUpdateVehicle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<VehicleFormValues> }) =>
      vehicleApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VEHICLES_KEY] });
      toast({ title: "Vehicle updated successfully" });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to update vehicle",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useDeleteVehicle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => vehicleApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VEHICLES_KEY] });
      toast({ title: "Vehicle deleted" });
    },
    onError: (error: any) => {
      toast({
        title: "Cannot delete vehicle",
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}