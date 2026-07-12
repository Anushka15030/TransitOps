export type VehicleType = "bus" | "mini_bus" | "van";
export type VehicleStatus = "active" | "maintenance" | "inactive";

export interface Vehicle {
  id: string;
  registration_number: string;
  vehicle_type: VehicleType;
  manufacturer: string;
  model: string;
  year: number;
  capacity: number;
  status: VehicleStatus;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface VehicleFilters {
  search?: string;
  vehicle_type?: VehicleType;
  status?: VehicleStatus;
  page: number;
  page_size: number;
}