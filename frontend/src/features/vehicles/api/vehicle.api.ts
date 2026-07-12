import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse, Vehicle, VehicleFilters } from "@/types/vehicle";
import type { VehicleFormValues } from "../schemas/vehicle.schema";

export const vehicleApi = {
  list: (filters: VehicleFilters) =>
    apiClient
      .get<PaginatedResponse<Vehicle>>("/vehicles", { params: filters })
      .then((res) => res.data),

  getById: (id: string) => apiClient.get<Vehicle>(`/vehicles/${id}`).then((res) => res.data),

  create: (payload: VehicleFormValues) =>
    apiClient.post<Vehicle>("/vehicles", payload).then((res) => res.data),

  update: (id: string, payload: Partial<VehicleFormValues>) =>
    apiClient.patch<Vehicle>(`/vehicles/${id}`, payload).then((res) => res.data),

  remove: (id: string) => apiClient.delete(`/vehicles/${id}`),
};