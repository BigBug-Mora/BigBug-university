import Link from "next/link";

export default function ListingNotFound() {
  return <div className="space-y-7"><h1>Listing unavailable</h1><p>This listing is not currently published.</p><Link href="/buyer/search">Back to Search</Link></div>;
}
