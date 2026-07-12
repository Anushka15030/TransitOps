import { PageHeader } from "@/components/layout/page-header";
import { DriverTable } from "@/features/drivers/components/driver-table";

export default function DriversPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Driver Management" description="Manage driver profiles, licenses, and availability" />
      <DriverTable />
    </div>
  );
}
