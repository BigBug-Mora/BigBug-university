import { notFound } from "next/navigation";
import { ProtectedView } from "@/app/protected-view";
import { listingPath } from "@/server/destinations";

export default async function ListingPage({ params }: { params: Promise<{ listingId: string }> }) {
  const { listingId } = await params;
  const destination = listingPath(listingId);
  if (!destination) notFound();
  return <ProtectedView destination={destination} title={`Listing ${listingId}`} />;
}
