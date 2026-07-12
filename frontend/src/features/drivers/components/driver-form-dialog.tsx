"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { useCreateDriver, useUpdateDriver } from "../hooks/useDrivers";
import {
  driverCreateSchema,
  driverUpdateSchema,
  type DriverCreateValues,
  type DriverUpdateValues,
} from "../schemas/driver.schema";
import type { Driver } from "@/types/driver";

interface DriverFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  driver?: Driver | null;
}

const CREATE_DEFAULTS: DriverCreateValues = {
  full_name: "",
  email: "",
  phone: "",
  password: "",
  license_number: "",
  license_expiry: "",
};

export function DriverFormDialog({ open, onOpenChange, driver }: DriverFormDialogProps) {
  const isEditMode = !!driver;
  const createDriver = useCreateDriver();
  const updateDriver = useUpdateDriver();
  const isSubmitting = createDriver.isPending || updateDriver.isPending;

  // Two separate forms (create needs email/phone/password, edit doesn't)
  // sharing one dialog shell — cleaner than one form with conditional
  // fields fighting a single Zod schema.
  const createForm = useForm<DriverCreateValues>({
    resolver: zodResolver(driverCreateSchema),
    defaultValues: CREATE_DEFAULTS,
  });

  const editForm = useForm<DriverUpdateValues>({
    resolver: zodResolver(driverUpdateSchema),
  });

  useEffect(() => {
    if (open) {
      if (driver) {
        editForm.reset({
          full_name: driver.full_name,
          license_number: driver.license_number,
          license_expiry: driver.license_expiry.split("T")[0],
          status: driver.status,
        });
      } else {
        createForm.reset(CREATE_DEFAULTS);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, driver]);

  const onCreateSubmit = (values: DriverCreateValues) => {
    createDriver.mutate(values, { onSuccess: () => onOpenChange(false) });
  };

  const onEditSubmit = (values: DriverUpdateValues) => {
    if (driver) {
      updateDriver.mutate({ id: driver.id, payload: values }, { onSuccess: () => onOpenChange(false) });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEditMode ? "Edit Driver" : "Add New Driver"}</DialogTitle>
        </DialogHeader>

        {isEditMode ? (
          <form onSubmit={editForm.handleSubmit(onEditSubmit)} className="space-y-4" noValidate>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input id="full_name" {...editForm.register("full_name")} />
              {editForm.formState.errors.full_name && (
                <p className="text-sm text-destructive">{editForm.formState.errors.full_name.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="license_number">License Number</Label>
                <Input id="license_number" {...editForm.register("license_number")} />
                {editForm.formState.errors.license_number && (
                  <p className="text-sm text-destructive">{editForm.formState.errors.license_number.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="license_expiry">License Expiry</Label>
                <Input id="license_expiry" type="date" {...editForm.register("license_expiry")} />
                {editForm.formState.errors.license_expiry && (
                  <p className="text-sm text-destructive">{editForm.formState.errors.license_expiry.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={editForm.watch("status")}
                onValueChange={(v) => editForm.setValue("status", v as DriverUpdateValues["status"])}
              >
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="on_trip">On Trip</SelectItem>
                  <SelectItem value="off_duty">Off Duty</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <form onSubmit={createForm.handleSubmit(onCreateSubmit)} className="space-y-4" noValidate>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input id="full_name" placeholder="Ramesh Kumar" {...createForm.register("full_name")} />
              {createForm.formState.errors.full_name && (
                <p className="text-sm text-destructive">{createForm.formState.errors.full_name.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="ramesh@transitops.com" {...createForm.register("email")} />
                {createForm.formState.errors.email && (
                  <p className="text-sm text-destructive">{createForm.formState.errors.email.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" placeholder="+91 98765 43210" {...createForm.register("phone")} />
                {createForm.formState.errors.phone && (
                  <p className="text-sm text-destructive">{createForm.formState.errors.phone.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Temporary Password</Label>
              <Input id="password" type="password" {...createForm.register("password")} />
              {createForm.formState.errors.password && (
                <p className="text-sm text-destructive">{createForm.formState.errors.password.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="license_number">License Number</Label>
                <Input id="license_number" placeholder="DL-1420110012345" {...createForm.register("license_number")} />
                {createForm.formState.errors.license_number && (
                  <p className="text-sm text-destructive">{createForm.formState.errors.license_number.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="license_expiry">License Expiry</Label>
                <Input id="license_expiry" type="date" {...createForm.register("license_expiry")} />
                {createForm.formState.errors.license_expiry && (
                  <p className="text-sm text-destructive">{createForm.formState.errors.license_expiry.message}</p>
                )}
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Add Driver"
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}