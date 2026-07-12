"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Pencil, Trash2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { StatusBadge } from "@/components/shared/status-badge";
import type { Driver } from "@/types/driver";

const EXPIRY_WARNING_DAYS = 30;

function isLicenseExpiringSoon(expiryDate: string): boolean {
  const diffDays = (new Date(expiryDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24);
  return diffDays <= EXPIRY_WARNING_DAYS;
}

interface DriverColumnsProps {
  onEdit: (driver: Driver) => void;
  onDelete: (driver: Driver) => void;
}

export function getDriverColumns({ onEdit, onDelete }: DriverColumnsProps): ColumnDef<Driver>[] {
  return [
    {
      id: "driver",
      header: "Driver",
      cell: ({ row }) => (
        <div>
          <p className="font-medium text-foreground">{row.original.full_name}</p>
          <p className="text-xs text-muted-foreground">{row.original.email}</p>
        </div>
      ),
    },
    {
      accessorKey: "phone",
      header: "Phone",
    },
    {
      accessorKey: "license_number",
      header: "License No.",
      cell: ({ row }) => (
        <span className="font-mono text-foreground">{row.original.license_number}</span>
      ),
    },
    {
      accessorKey: "license_expiry",
      header: "License Expiry",
      cell: ({ row }) => {
        const expiring = isLicenseExpiringSoon(row.original.license_expiry);
        return (
          <div className="flex items-center gap-1.5">
            <span className={expiring ? "text-amber-400" : "text-foreground"}>
              {new Date(row.original.license_expiry).toLocaleDateString()}
            </span>
            {expiring && <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />}
          </div>
        );
      },
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