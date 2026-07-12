import { z } from "zod";

export const tripCreateSchema = z
  .object({
    route_id: z.string().min(1, "Select a route"),
    vehicle_id: z.string().min(1, "Select a vehicle"),
    driver_id: z.string().min(1, "Select a driver"),
    departure_time: z.string().min(1, "Departure time is required"),
    arrival_time: z.string().min(1, "Arrival time is required"),
    available_seats: z.coerce.number().int().positive("Must be greater than 0"),
    fare: z.coerce.number().min(0, "Fare cannot be negative"),
  })
  .refine((data) => new Date(data.arrival_time) > new Date(data.departure_time), {
    message: "Arrival time must be after departure time",
    path: ["arrival_time"],
  });

export type TripCreateValues = z.infer<typeof tripCreateSchema>;