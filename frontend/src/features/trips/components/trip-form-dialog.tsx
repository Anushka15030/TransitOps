"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { useActiveVehicleOptions, useAvailableDriverOptions, useCreateTrip, useRouteOptions } from "../hooks/useTrips";
import { tripCreateSchema, type TripCreateValues } from "../schemas/trip.schema";

interface TripFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TripFormDialog({ open, onOpenChange }: TripFormDialogProps) {
  const createTrip = useCreateTrip();
  const { data: routes } = useRouteOptions();
  const { data: vehicles } = useActiveVehicleOptions();
  const { data: drivers } = useAvailableDriverOptions();

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<TripCreateValues>({
    resolver: zodResolver(tripCreateSchema),
  });

  useEffect(() => {
    if (open) reset();
  }, [open, reset]);

  const onSubmit = (values: TripCreateValues) => {
    createTrip.mutate(values, { onSuccess: () => onOpenChange(false) });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create Trip (Draft)</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label>Route</Label>
            <Select onValueChange={(v) => setValue("route_id", v)}>
              <SelectTrigger><SelectValue placeholder="Select a route" /></SelectTrigger>
              <SelectContent>
                {routes?.map((r) => (
                  <SelectItem key={r.id} value={r.id}>{r.name} ({r.origin} → {r.destination})</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.route_id && <p className="text-sm text-destructive">{errors.route_id.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Vehicle</Label>
              <Select onValueChange={(v) => setValue("vehicle_id", v)}>
                <SelectTrigger><SelectValue placeholder="Select vehicle" /></SelectTrigger>
                <SelectContent>
                  {vehicles?.map((v) => (
                    <SelectItem key={v.id} value={v.id}>{v.registration_number} ({v.capacity} seats)</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.vehicle_id && <p className="text-sm text-destructive">{errors.vehicle_id.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Driver</Label>
              <Select onValueChange={(v) => setValue("driver_id", v)}>
                <SelectTrigger><SelectValue placeholder="Select driver" /></SelectTrigger>
                <SelectContent>
                  {drivers?.map((d) => (
                    <SelectItem key={d.id} value={d.id}>{d.full_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.driver_id && <p className="text-sm text-destructive">{errors.driver_id.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Departure</Label>
              <Input type="datetime-local" {...register("departure_time")} />
              {errors.departure_time && <p className="text-sm text-destructive">{errors.departure_time.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Arrival</Label>
              <Input type="datetime-local" {...register("arrival_time")} />
              {errors.arrival_time && <p className="text-sm text-destructive">{errors.arrival_time.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Available Seats</Label>
              <Input type="number" {...register("available_seats")} />
              {errors.available_seats && <p className="text-sm text-destructive">{errors.available_seats.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Fare (₹)</Label>
              <Input type="number" step="0.01" {...register("fare")} />
              {errors.fare && <p className="text-sm text-destructive">{errors.fare.message}</p>}
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={createTrip.isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={createTrip.isPending}>
              {createTrip.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating...</>
              ) : "Create Draft"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}