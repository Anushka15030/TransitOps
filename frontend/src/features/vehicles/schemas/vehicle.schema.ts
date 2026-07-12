import { z } from "zod";

const CURRENT_YEAR_CEILING = 2027;

export const vehicleFormSchema = z.object({
  registration_number: z
    .string()
    .min(3, "Registration number is too short")
    .max(20, "Registration number is too long")
    .regex(/^[A-Za-z0-9-]+$/, "Only letters, numbers and hyphens allowed"),
  vehicle_type: z.enum(["bus", "mini_bus", "van"], { required_error: "Select a vehicle type" }),
  manufacturer: z.string().min(1, "Manufacturer is required").max(100),
  model: z.string().min(1, "Model is required").max(100),
  year: z.coerce
    .number()
    .int("Year must be a whole number")
    .min(1990, "Year must be 1990 or later")
    .max(CURRENT_YEAR_CEILING, `Year cannot exceed ${CURRENT_YEAR_CEILING}`),
  capacity: z.coerce
    .number()
    .int("Capacity must be a whole number")
    .positive("Capacity must be greater than 0")
    .max(200, "Capacity seems unrealistically high"),
  status: z.enum(["active", "maintenance", "inactive"]),
});

export type VehicleFormValues = z.infer<typeof vehicleFormSchema>;