export type MaintenanceStatus = "open" | "closed";

export interface MaintenanceRecord {
  id: string;
  vehicle_id: string;
  vehicle_registration: string;
  reported_issue: string;
  status: MaintenanceStatus;
  opened_at: string;
  closed_at: string | null;
  resolution_notes: string | null;
  estimated_cost: number | null;
  created_at: string;
}

export interface MaintenanceFilters {
  status?: MaintenanceStatus;
  vehicle_id?: string;
  page: number;
  page_size: number;
}