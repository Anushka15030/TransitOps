"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

import { useCloseMaintenance } from "../hooks/useMaintenance";
import { closeMaintenanceSchema, type CloseMaintenanceValues } from "../schemas/maintenance.schema";
import type { MaintenanceRecord } from "@/types/maintenance";

interface CloseMaintenanceDialogProps {
  record: MaintenanceRecord | null;
  onOpenChange: (open: boolean) => void;
}

export function CloseMaintenanceDialog({ record, onOpenChange }: CloseMaintenanceDialogProps) {
  const closeMaintenance = useCloseMaintenance();
  const { register, handleSubmit, formState: { errors } } = useForm<CloseMaintenanceValues>({
    resolver: zodResolver(closeMaintenanceSchema),
  });

  const onSubmit = (values: CloseMaintenanceValues) => {
    if (record) {
      closeMaintenance.mutate({ id: record.id, payload: values }, { onSuccess: () => onOpenChange(false) });
    }
  };

  return (
    <Dialog open={!!record} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Close Maintenance — {record?.vehicle_registration}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="rounded-md border border-border bg-muted/30 p-3 text-sm text-muted-foreground">
            {record?.reported_issue}
          </div>

          <div className="space-y-2">
            <Label>Resolution Notes</Label>
            <Textarea rows={3} placeholder="Replaced brake pads, cleared warning light..." {...register("resolution_notes")} />
            {errors.resolution_notes && <p className="text-sm text-destructive">{errors.resolution_notes.message}</p>}
          </div>

          <div className="space-y-2">
            <Label>Actual Cost (₹, optional)</Label>
            <Input type="number" step="0.01" {...register("actual_cost")} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={closeMaintenance.isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={closeMaintenance.isPending}>
              {closeMaintenance.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Closing...</>
              ) : "Close & Return to Service"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}