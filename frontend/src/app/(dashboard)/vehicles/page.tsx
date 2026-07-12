import { PageHeader } from "@/components/layout/page-header";
import { VehicleTable } from "@/features/vehicles/components/vehicle-table";

export default function VehiclesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Vehicle Management"
        description="Manage your fleet of buses, mini-buses, and vans"
      />
      <VehicleTable />
    </div>
  );
}