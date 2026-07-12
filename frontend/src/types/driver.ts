export type DriverStatus = "available" | "on_trip" | "off_duty" | "suspended";

export interface Driver {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone: string;
  license_number: string;
  license_expiry: string; // ISO date string
  status: DriverStatus;
  created_at: string;
  updated_at: string;
}

export interface DriverFilters {
  search?: string;
  status?: DriverStatus;
  page: number;
  page_size: number;
}