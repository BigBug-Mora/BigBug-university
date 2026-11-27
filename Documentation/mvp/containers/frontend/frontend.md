# Frontend Container

[Container directory](../containers.md) · [MVP agent behavior](../../agent-details/agent-details.md)

## Runtime and responsibilities

Run the Next.js, React, TypeScript, and Tailwind application. The Next.js server runs in the container. The browser renders screens and submits user actions. Use Cognito for sign-in, with the Auth.js integration described in the [tech stack](../../teach-stack/tech-stack.md).

| Area | User actions and states |
| --- | --- |
| Seller | Create and edit a draft for a house, land, or apartment. Upload photos and review optional inspection suggestions. Use Save draft for a private save or Save and generate showcase to generate from that saved revision. Offer Regenerate showcase in the editor after facts change. Preview, edit and explicitly publish the matching revision and showcase. |
| Seller inbox | View a current summary grouped by property and underlying missing fact. Review, approve, decline, or leave an item pending. Handle phone and location requests independently. |
| Buyer | Sign in, search in natural language, browse published results, open a listing, and enter its Property Chat. Back to Search restores the previous query and results. |
| Private details | Use the same request actions on the property page and in chat. In the dedicated result, show pending or declined status, the current values the seller has shared, or an unavailable state for a removed detail. In the seller editor, explain that editing a shared detail updates it for existing recipients. Removing the detail ends access through that detail ID. |

## Data and service calls

- Call [Property service](../property-service/property-service.md) for listing views, edits, publication, and authorized S3 transfers. Show progress and failures for individual uploads. A successful file transfer still needs a successful metadata registration before that photo appears in the draft.
- On the property detail page, show the cover and key public facts near the top, up to three photo write-ups in story order, and the full gallery at the bottom. Keep featured photos in the gallery. Show the published property facts directly on the page and provide Property Chat for follow-up questions.
- Call [Engagement service](../engagement-service/engagement-service.md) for chat history, inbox records, confirmed questions, seller decisions, and disclosure results. Reload persisted messages from the authorized conversation when the browser refreshes. Use the selected listing and conversation IDs as navigation context. The backend validates the association.
- Call [Agent API](../agent-api/agent-api.md) for interactive replies and to request inspection or showcase work. Show pending, running, ready, and failed states from durable job status. Recover status after refresh.
- Keep form edits, progress indicators, and other transient state in the UI as appropriate. Unsent text is a local draft only if draft persistence is explicitly implemented. A completed chat turn and a pending inquiry are backed by server data.

## Permissions and failures

Require buyers to sign in before searching or opening a published listing, including from a direct link. After sign-in, resume the requested search page or listing. Require sellers to sign in before opening the seller workspace.

Use server-side session handling for backend calls. Cognito, backend credentials, and public configuration have different audiences. Store secrets server-side and keep protected results out of shared caches, logs, and analytics. Display a dedicated phone or location result only after the backend returns it for the signed-in buyer.

Handle session expiration, forbidden access, missing listings, job failures, and network errors explicitly. Use the same action identifier when retrying an ambiguous submission so a refresh or double click does not create a second chat turn or request. Keep the active listing scope visible in Property Chat.

Verify chat refresh, Back to Search, upload retry, preservation of the published listing while a showcase draft is reviewed, and private-detail access for two different buyers. Streaming versus a complete response, unfinished-turn indicators after refresh, and polling versus pushed status updates are open contracts.
