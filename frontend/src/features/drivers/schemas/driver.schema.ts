import { z } from "zod";

export const driverCreateSchema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters").max(150),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(7, "Enter a valid phone number").max(20),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain an uppercase letter")
    .regex(/[0-9]/, "Must contain a digit"),
  license_number: z
    .string()
    .min(3, "License number is too short")
    .max(50)
    .regex(/^[A-Za-z0-9-]+$/, "Only letters, numbers and hyphens allowed"),
  license_expiry: z
    .string()
    .min(1, "License expiry date is required")
    .refine((val) => new Date(val) > new Date(), "Expiry date must be in the future"),
});
export type DriverCreateValues = z.infer<typeof driverCreateSchema>;

export const driverUpdateSchema = z.object({
  full_name: z.string().min(2).max(150).optional(),
  license_number: z
    .string()
    .min(3)
    .max(50)
    .regex(/^[A-Za-z0-9-]+$/, "Only letters, numbers and hyphens allowed")
    .optional(),
  license_expiry: z
    .string()
    .refine((val) => !val || new Date(val) > new Date(), "Expiry date must be in the future")
    .optional(),
  status: z.enum(["available", "on_trip", "off_duty", "suspended"]).optional(),
});
export type DriverUpdateValues = z.infer<typeof driverUpdateSchema>;