import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/api";
import type { Driver, DriverFilters } from "@/types/driver";
import type { DriverCreateValues, DriverUpdateValues } from "../schemas/driver.schema";

export const driverApi = {
  list: (filters: DriverFilters) =>
    apiClient.get<PaginatedResponse<Driver>>("/drivers", { params: filters }).then((res) => res.data),

  getById: (id: string) => apiClient.get<Driver>(`/drivers/${id}`).then((res) => res.data),

  create: (payload: DriverCreateValues) =>
    apiClient.post<Driver>("/drivers", payload).then((res) => res.data),

  update: (id: string, payload: DriverUpdateValues) =>
    apiClient.patch<Driver>(`/drivers/${id}`, payload).then((res) => res.data),

  remove: (id: string) => apiClient.delete(`/drivers/${id}`),
};