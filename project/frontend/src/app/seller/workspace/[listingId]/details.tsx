"use client";

import { useRouter } from "next/navigation";
import { updateDetail, removeDetail } from "../actions";
import { Feedback, useSubmission } from "../submission";

export type Detail = {id:string; detail_kind:string; slot_no:number; retired_at:string|null; updated_at:string; value?:string|{latitude:string; longitude:string}};

function Slot({listing,kind,slot,detail}: {listing:string; kind:string; slot:number; detail?:Detail}) {
  const submit = useSubmission();
  const router = useRouter();
  const name = kind==="phone" ? "Phone " + slot : kind==="map_pin" ? "Map pin" : "Written address";
  const pin = typeof detail?.value==="object" ? detail.value : undefined;
  return <form onSubmit={event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    void submit.run(async () => {
      const value = kind==="map_pin" ? {latitude:data.get("latitude"), longitude:data.get("longitude")} : data.get("value");
      const result = await updateDetail(listing,kind,slot,value);
      if (!result.ok) return submit.setMessage(result.message);
      submit.setMessage("Detail saved.");
      router.refresh();
    });
  }}><fieldset><legend>{name}</legend>{kind==="map_pin" ? <>
    <label>Latitude<input type="number" step="any" min="-90" max="90" name="latitude" required defaultValue={pin?.latitude}/></label>
    <label>Longitude<input type="number" step="any" min="-180" max="180" name="longitude" required defaultValue={pin?.longitude}/></label></> :
    <label>{name}<input type={kind==="phone"?"tel":"text"} name="value" required defaultValue={typeof detail?.value==="string"?detail.value:""}/></label>}
    <button className="button" disabled={submit.busy}>Save {name.toLowerCase()}</button>
    {detail && <button className="button" type="button" disabled={submit.busy} onClick={() => void submit.run(async () => {
      const result = await removeDetail(listing,detail.id);
      if (!result.ok) return submit.setMessage(result.message);
      submit.setMessage("Detail removed.");
      router.refresh();
    })}>Remove {name.toLowerCase()}</button>}</fieldset><Feedback message={submit.message}/></form>;
}

export function Details({listing,details}: {listing:string;details:Detail[]}) {
  return <section><h2>Private details</h2><p>Editing a shared detail updates it for existing recipients.
    Removing it retires its ID and ends their access. Adding it again requires a new grant.</p>
    {["phone","phone","phone","written_address","map_pin"].map((kind,i) => {
      const slot = kind==="phone"?i+1:1;
      const detail = details.find(d => !d.retired_at && d.detail_kind===kind && d.slot_no===slot);
      return <Slot key={detail?.id ?? kind+slot} listing={listing} kind={kind} slot={slot} detail={detail}/>;
    })}</section>;
}
