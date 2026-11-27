import Link from "next/link";
import { protectedAccount } from "@/server/session";
import { propertyRequest } from "@/server/property";
import { Editor, type Revision, type Width } from "./editor";
import { Details, type Detail } from "./details";

export default async function ListingPage({
  params,
}: {
  params: Promise<{ listingId: string }>;
}) {
  const { listingId } = await params;
  if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(listingId))
    return <h1>Listing unavailable</h1>;
  const actor = await protectedAccount("/seller/workspace/" + listingId);
  if (actor.status !== "active")
    return (
      <h1>
        {actor.status === "forbidden"
          ? "Access denied"
          : "Service temporarily unavailable"}
      </h1>
    );
  const [draft, details] = await Promise.all([
    propertyRequest<{
      revision: Revision;
      facts: (Width & { fact_key: string })[];
    }>("/" + listingId),
    propertyRequest<Detail[]>("/" + listingId + "/private-details"),
  ]);
  return (
    <div className="workspace">
      <Link href="/seller/workspace">Back to seller workspace</Link>
      {!draft.ok ? (
        <h1>{draft.message}</h1>
      ) : (
        <>
          <h1>{draft.data.revision.property_type} draft</h1>
          <Editor
            listing={listingId}
            revision={draft.data.revision}
            width={draft.data.facts.find(
              (f) => f.fact_key === "access_road_width",
            )}
          />
          {details.ok ? (
            <Details listing={listingId} details={details.data} />
          ) : (
            <p role="alert">{details.message}</p>
          )}
        </>
      )}
    </div>
  );
}
