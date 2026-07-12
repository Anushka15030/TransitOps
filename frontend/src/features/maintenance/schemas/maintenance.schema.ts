import { z } from "zod";

export const openMaintenanceSchema = z.object({
  vehicle_id: z.string().min(1, "Select a vehicle"),
  reported_issue: z.string().min(5, "Describe the issue (min 5 characters)").max(2000),
  estimated_cost: z.coerce.number().min(0).optional(),
});
export type OpenMaintenanceValues = z.infer<typeof openMaintenanceSchema>;

export const closeMaintenanceSchema = z.object({
  resolution_notes: z.string().min(5, "Describe the resolution (min 5 characters)").max(2000),
  actual_cost: z.coerce.number().min(0).optional(),
});
export type CloseMaintenanceValues = z.infer<typeof closeMaintenanceSchema>;