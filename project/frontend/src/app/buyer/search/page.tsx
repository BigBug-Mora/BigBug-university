import { ProtectedView } from "@/app/protected-view";
import { buyerSearch } from "@/server/destinations";

export default function SearchPage() {
  return <ProtectedView destination={buyerSearch} title="Buyer search" />;
}
