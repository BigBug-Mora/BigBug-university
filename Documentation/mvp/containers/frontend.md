# Frontend Container

[Container directory](containers.md) · [MVP agent behavior](../agent-details/agent-details.md)

## Runtime and responsibilities

Run the Next.js, React, TypeScript, and Tailwind application. The Next.js server runs in the container. The browser renders screens and submits user actions. Use Cognito for sign-in, with the Auth.js integration described in the [tech stack](../teach-stack/tech-stack.md).

| Area | User actions and states |
| --- | --- |
| Seller | Create and edit a draft for a house, land, or apartment. Upload photos. See inspection suggestions, choose whether to act on them, edit a showcase, and explicitly publish. |
| Seller inbox | View a current summary grouped by property and underlying missing fact. Review, approve, decline, or leave an item pending. Handle phone and location requests independently. |
| Buyer | Search in natural language, browse published results, open a listing, and enter its Property Chat. Back to Search restores the previous query and results. |
| Private details | Show the same request actions on the property page and when offered in chat. Show pending or declined status and reveal an approved value only in its dedicated result. |

## Data and service calls

- Call [Property service](property-service.md) for listing views, edits, publication, and authorized S3 transfers. Show progress and failures for individual uploads. A successful file transfer still needs a successful metadata registration before that photo appears in the draft.
- Call [Engagement service](engagement-service.md) for chat history, inbox records, confirmed questions, seller decisions, and disclosure results. Reload persisted messages from the authorized conversation when the browser refreshes. Use the selected listing and conversation IDs as navigation context. The backend validates the association.
- Call [Agent API](agent-api/agent-api.md) for interactive replies and to request inspection or showcase work. Show pending, running, ready, and failed states from durable job status. Recover status after refresh.
- Keep form edits, progress indicators, and other transient state in the UI as appropriate. Unsent text is a local draft only if draft persistence is explicitly implemented. A completed chat turn and a pending inquiry are backed by server data.

## Permissions and failures

Use server-side session handling for backend calls. Cognito, backend credentials, and public configuration have different audiences. Store secrets server-side and keep protected results out of shared caches, logs, and analytics. Display a dedicated phone or location result only after the backend returns it for the signed-in buyer.

Handle session expiration, forbidden access, missing listings, job failures, and network errors explicitly. Use the same action identifier when retrying an ambiguous submission so a refresh or double click does not create a second chat turn or request. Keep the active listing scope visible in Property Chat.

Verify chat refresh, Back to Search, upload retry, preservation of the published listing while a showcase draft is reviewed, and private-detail access for two different buyers. Streaming versus a complete response, unfinished-turn indicators after refresh, and polling versus pushed status updates are open contracts.
