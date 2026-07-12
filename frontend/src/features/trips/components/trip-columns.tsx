"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Rocket, CheckCircle2, XCircle, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { StatusBadge } from "@/components/shared/status-badge";
import type { Trip } from "@/types/trip";

interface TripColumnsProps {
  onDispatch: (trip: Trip) => void;
  onComplete: (trip: Trip) => void;
  onCancel: (trip: Trip) => void;
  onDelete: (trip: Trip) => void;
}

export function getTripColumns({ onDispatch, onComplete, onCancel, onDelete }: TripColumnsProps): ColumnDef<Trip>[] {
  return [
    {
      id: "route",
      header: "Route",
      cell: ({ row }) => <span className="font-medium text-foreground">{row.original.route_name}</span>,
    },
    {
      id: "vehicle",
      header: "Vehicle",
      cell: ({ row }) => <span className="font-mono text-sm">{row.original.vehicle_registration}</span>,
    },
    {
      id: "driver",
      header: "Driver",
      cell: ({ row }) => row.original.driver_name,
    },
    {
      id: "schedule",
      header: "Schedule",
      cell: ({ row }) => (
        <div className="text-sm">
          <p className="text-foreground">{new Date(row.original.departure_time).toLocaleString()}</p>
          <p className="text-xs text-muted-foreground">
            → {new Date(row.original.arrival_time).toLocaleString()}
          </p>
        </div>
      ),
    },
    {
      accessorKey: "fare",
      header: "Fare",
      cell: ({ row }) => `₹${row.original.fare.toFixed(2)}`,
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => {
        const trip = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {trip.status === "draft" && (
                <>
                  <DropdownMenuItem onClick={() => onDispatch(trip)}>
                    <Rocket className="mr-2 h-4 w-4" />
                    Dispatch
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onDelete(trip)} className="text-destructive focus:text-destructive">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete Draft
                  </DropdownMenuItem>
                </>
              )}
              {trip.status === "dispatched" && (
                <DropdownMenuItem onClick={() => onComplete(trip)}>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Mark Completed
                </DropdownMenuItem>
              )}
              {(trip.status === "draft" || trip.status === "dispatched") && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => onCancel(trip)} className="text-destructive focus:text-destructive">
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancel Trip
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
}