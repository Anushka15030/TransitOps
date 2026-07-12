"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { StatusBadge } from "@/components/shared/status-badge";
import type { Vehicle } from "@/types/vehicle";

const VEHICLE_TYPE_LABELS: Record<string, string> = {
  bus: "Bus",
  mini_bus: "Mini Bus",
  van: "Van",
};

interface VehicleColumnsProps {
  onEdit: (vehicle: Vehicle) => void;
  onDelete: (vehicle: Vehicle) => void;
}

export function getVehicleColumns({ onEdit, onDelete }: VehicleColumnsProps): ColumnDef<Vehicle>[] {
  return [
    {
      accessorKey: "registration_number",
      header: "Registration No.",
      cell: ({ row }) => (
        <span className="font-mono font-medium text-foreground">
          {row.original.registration_number}
        </span>
      ),
    },
    {
      accessorKey: "vehicle_type",
      header: "Type",
      cell: ({ row }) => VEHICLE_TYPE_LABELS[row.original.vehicle_type],
    },
    {
      id: "vehicle",
      header: "Vehicle",
      cell: ({ row }) => (
        <div>
          <p className="text-foreground">{row.original.manufacturer} {row.original.model}</p>
          <p className="text-xs text-muted-foreground">{row.original.year}</p>
        </div>
      ),
    },
    {
      accessorKey: "capacity",
      header: "Capacity",
      cell: ({ row }) => `${row.original.capacity} seats`,
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(row.original)}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(row.original)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];
}