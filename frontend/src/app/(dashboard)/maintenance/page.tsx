import { PageHeader } from "@/components/layout/page-header";
import { MaintenanceTable } from "@/features/maintenance/components/maintenance-table";

export default function MaintenancePage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Vehicle Maintenance" description="Track vehicles in the shop and their return to service" />
      <MaintenanceTable />
    </div>
  );
}