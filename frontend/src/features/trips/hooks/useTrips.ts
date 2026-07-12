"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/hooks/use-toast";
import type { TripFilters } from "@/types/trip";
import { tripApi } from "../api/trip.api";
import type { TripCreateValues } from "../schemas/trip.schema";

const TRIPS_KEY = "trips";

export function useTrips(filters: TripFilters) {
  return useQuery({
    queryKey: [TRIPS_KEY, filters],
    queryFn: () => tripApi.list(filters),
    placeholderData: (prev) => prev,
  });
}

export function useRouteOptions() {
  return useQuery({ queryKey: ["route-options"], queryFn: tripApi.routeOptions });
}
export function useActiveVehicleOptions() {
  return useQuery({ queryKey: ["active-vehicle-options"], queryFn: tripApi.activeVehicleOptions });
}
export function useAvailableDriverOptions() {
  return useQuery({ queryKey: ["available-driver-options"], queryFn: tripApi.availableDriverOptions });
}

function useTripMutation<T>(
  mutationFn: (arg: T) => Promise<any>,
  successMessage: string,
  errorTitle: string
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TRIPS_KEY] });
      toast({ title: successMessage });
    },
    onError: (error: any) => {
      toast({
        title: errorTitle,
        description: error?.response?.data?.error?.message ?? "Please try again",
        variant: "destructive",
      });
    },
  });
}

export function useCreateTrip() {
  return useTripMutation((payload: TripCreateValues) => tripApi.create(payload), "Trip created as draft", "Failed to create trip");
}
export function useDispatchTrip() {
  return useTripMutation((id: string) => tripApi.dispatch(id), "Trip dispatched successfully", "Cannot dispatch trip");
}
export function useCompleteTrip() {
  return useTripMutation((id: string) => tripApi.complete(id), "Trip marked as completed", "Cannot complete trip");
}
export function useCancelTrip() {
  return useTripMutation(
    ({ id, reason }: { id: string; reason?: string }) => tripApi.cancel(id, reason),
    "Trip cancelled",
    "Cannot cancel trip"
  );
}
export function useDeleteTrip() {
  return useTripMutation((id: string) => tripApi.remove(id), "Draft trip deleted", "Cannot delete trip");
}