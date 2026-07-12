import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/api";
import type { RouteOption, Trip, TripFilters } from "@/types/trip";
import type { Vehicle } from "@/types/vehicle";
import type { Driver } from "@/types/driver";
import type { TripCreateValues } from "../schemas/trip.schema";

export const tripApi = {
  list: (filters: TripFilters) =>
    apiClient.get<PaginatedResponse<Trip>>("/trips", { params: filters }).then((res) => res.data),

  getById: (id: string) => apiClient.get<Trip>(`/trips/${id}`).then((res) => res.data),

  create: (payload: TripCreateValues) => apiClient.post<Trip>("/trips", payload).then((res) => res.data),

  update: (id: string, payload: Partial<TripCreateValues>) =>
    apiClient.patch<Trip>(`/trips/${id}`, payload).then((res) => res.data),

  remove: (id: string) => apiClient.delete(`/trips/${id}`),

  dispatch: (id: string) => apiClient.post(`/trips/${id}/dispatch`).then((res) => res.data),
  complete: (id: string) => apiClient.post(`/trips/${id}/complete`).then((res) => res.data),
  cancel: (id: string, reason?: string) =>
    apiClient.post(`/trips/${id}/cancel`, { reason }).then((res) => res.data),

  // Dropdown sources
  routeOptions: () => apiClient.get<RouteOption[]>("/routes/options").then((res) => res.data),
  activeVehicleOptions: () => apiClient.get<Vehicle[]>("/vehicles/options/active").then((res) => res.data),
  availableDriverOptions: () => apiClient.get<Driver[]>("/drivers/options/available").then((res) => res.data),
};