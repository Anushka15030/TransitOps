import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/api";
import type { MaintenanceFilters, MaintenanceRecord } from "@/types/maintenance";
import type { CloseMaintenanceValues, OpenMaintenanceValues } from "../schemas/maintenance.schema";

export const maintenanceApi = {
  list: (filters: MaintenanceFilters) =>
    apiClient.get<PaginatedResponse<MaintenanceRecord>>("/maintenance", { params: filters }).then((r) => r.data),

  open: (payload: OpenMaintenanceValues) =>
    apiClient.post<MaintenanceRecord>("/maintenance", payload).then((r) => r.data),

  close: (id: string, payload: CloseMaintenanceValues) =>
    apiClient.post<MaintenanceRecord>(`/maintenance/${id}/close`, payload).then((r) => r.data),
};