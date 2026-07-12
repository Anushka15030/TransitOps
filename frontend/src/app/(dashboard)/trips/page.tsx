import { PageHeader } from "@/components/layout/page-header";
import { TripTable } from "@/features/trips/components/trip-table";

export default function TripsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Trip Management" description="Draft, dispatch, and track trips across your fleet" />
      <TripTable />
    </div>
  );
}