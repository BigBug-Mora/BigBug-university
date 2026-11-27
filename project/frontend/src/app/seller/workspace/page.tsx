import { ProtectedView } from "@/app/protected-view";
import { sellerWorkspace } from "@/server/destinations";

export default function SellerPage() {
  return <ProtectedView destination={sellerWorkspace} title="Seller workspace" />;
}
