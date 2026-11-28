import Link from "next/link";
import { ListingShowcase } from "@/components/listing-showcase";
import { previewView, type PreviewState } from "@/components/listing-types";
import { protectedAccount } from "@/server/session";
import { propertyRequest } from "@/server/property";
import { PublicationControls } from "../publication-controls";

export default async function PreviewPage({ params }: { params: Promise<{ listingId: string }> }) {
  const { listingId } = await params;
  const actor = await protectedAccount(`/seller/workspace/${listingId}/preview`);
  if (actor.status !== "active") return <h1>{actor.status === "forbidden" ? "Access denied" : "Service temporarily unavailable"}</h1>;
  if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(listingId)) return <h1>Listing unavailable</h1>;
  const result = await propertyRequest<PreviewState>(`/${listingId}/showcase`);
  if (!result.ok) return <h1>{result.message}</h1>;
  const view = previewView(result.data);
  return <div className="showcase">
    <aside className="showcase-banner"><strong>Seller preview · Not a publication</strong><Link href={`/seller/workspace/${listingId}`}>Back to listing editor</Link></aside>
    {view ? <ListingShowcase listing={view} /> : <div><h1>Showcase needs updating</h1><p>Save showcase copy for the current draft in the listing editor.</p></div>}
    <div className="workspace"><PublicationControls state={result.data} /></div>
  </div>;
}
