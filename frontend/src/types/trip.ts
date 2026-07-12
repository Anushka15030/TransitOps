export type TripStatus = "draft" | "dispatched" | "completed" | "cancelled";

export interface Trip {
  id: string;
  route_id: string;
  route_name: string;
  vehicle_id: string;
  vehicle_registration: string;
  driver_id: string;
  driver_name: string;
  departure_time: string;
  arrival_time: string;
  available_seats: number;
  fare: number;
  status: TripStatus;
  created_at: string;
  updated_at: string;
}

export interface TripFilters {
  status?: TripStatus;
  route_id?: string;
  vehicle_id?: string;
  driver_id?: string;
  page: number;
  page_size: number;
}

export interface RouteOption {
  id: string;
  name: string;
  origin: string;
  destination: string;
}