import Link from "next/link";
import { buyerSearch, sellerWorkspace } from "@/server/destinations";

export default function LandingPage() {
  return (
    <div className="space-y-7">
      <h1>Find or list a property</h1>
      <p>Sign in to search listings or open your seller workspace.</p>
      <div className="flex flex-wrap gap-3">
        <Link href={buyerSearch} className="button button-primary" prefetch={false}>
          Continue as buyer
        </Link>
        <Link href={sellerWorkspace} className="button" prefetch={false}>
          Continue as seller
        </Link>
      </div>
    </div>
  );
}
