"use client";

import { useRef, useState } from "react";

export function useSubmission() {
  const lock = useRef(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function run(operation: () => Promise<void>) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setMessage("");
    try {
      await operation();
    } catch {
      setMessage("The save could not be confirmed. Try again.");
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return { busy, message, setMessage, run };
}

export async function actionId(scope: string, submission: unknown) {
  const bytes = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(JSON.stringify(submission)),
  );
  const fingerprint = Array.from(new Uint8Array(bytes), (n) =>
    n.toString(16).padStart(2, "0"),
  ).join("");
  const key = "estateflow-draft:" + scope + ":" + fingerprint;
  const id = sessionStorage.getItem(key) ?? crypto.randomUUID();
  sessionStorage.setItem(key, id);
  return { id, complete: () => sessionStorage.removeItem(key) };
}

export function Feedback({ message }: { message: string }) {
  return (
    <div role="status">
      {message}{" "}
      {message.includes("session expired") && (
        <a
          href={`/sign-in?returnTo=${encodeURIComponent(location.pathname)}`}
          target="_blank"
          rel="noreferrer"
        >
          Sign in again
        </a>
      )}
      {message.includes("Another revision") && (
        <a href={location.pathname} target="_blank" rel="noreferrer">
          Open current revision
        </a>
      )}
    </div>
  );
}
