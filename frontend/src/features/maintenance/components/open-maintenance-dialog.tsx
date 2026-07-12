"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { useVehicles } from "@/features/vehicles/hooks/useVehicles";
import { useOpenMaintenance } from "../hooks/useMaintenance";
import { openMaintenanceSchema, type OpenMaintenanceValues } from "../schemas/maintenance.schema";

interface OpenMaintenanceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function OpenMaintenanceDialog({ open, onOpenChange }: OpenMaintenanceDialogProps) {
  const openMaintenance = useOpenMaintenance();
  // Only offer ACTIVE vehicles — one already in maintenance shouldn't be selectable again
  const { data: vehiclesPage } = useVehicles({ status: "active", page: 1, page_size: 100 });

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<OpenMaintenanceValues>({
    resolver: zodResolver(openMaintenanceSchema),
  });

  const onSubmit = (values: OpenMaintenanceValues) => {
    openMaintenance.mutate(values, { onSuccess: () => onOpenChange(false) });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Move Vehicle to Maintenance</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label>Vehicle</Label>
            <Select onValueChange={(v) => setValue("vehicle_id", v)}>
              <SelectTrigger><SelectValue placeholder="Select vehicle" /></SelectTrigger>
              <SelectContent>
                {vehiclesPage?.items.map((v) => (
                  <SelectItem key={v.id} value={v.id}>{v.registration_number} — {v.manufacturer} {v.model}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.vehicle_id && <p className="text-sm text-destructive">{errors.vehicle_id.message}</p>}
          </div>

          <div className="space-y-2">
            <Label>Reported Issue</Label>
            <Textarea rows={3} placeholder="Engine warning light, brake inspection due..." {...register("reported_issue")} />
            {errors.reported_issue && <p className="text-sm text-destructive">{errors.reported_issue.message}</p>}
          </div>

          <div className="space-y-2">
            <Label>Estimated Cost (₹, optional)</Label>
            <Input type="number" step="0.01" {...register("estimated_cost")} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={openMaintenance.isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={openMaintenance.isPending}>
              {openMaintenance.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Submitting...</>
              ) : "Move to Maintenance"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}