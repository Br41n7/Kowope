"use client";

import { useEffect, useState } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { Field, TextInput } from "@/components/Field";
import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { createOffer, listRFQs, unwrap } from "@/lib/endpoints";
import type { RFQ } from "@/lib/types";
import { ApiError } from "@/lib/api";

function OfferForm({ rfq, onSubmitted }: { rfq: RFQ; onSubmitted: () => void }) {
  const [price, setPrice] = useState("");
  const [period, setPeriod] = useState("");
  const [cert, setCert] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await createOffer({ rfq: rfq.id, price, delivery_period: period, quality_certs: cert });
      setOpen(false);
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.body) : "Could not submit offer.");
    } finally {
      setBusy(false);
    }
  };

  if (!open) {
    return <Button onClick={() => setOpen(true)}>Make an offer</Button>;
  }

  return (
    <form onSubmit={onSubmit} className="mt-2 flex flex-wrap items-end gap-3">
      <Field label="Your price">
        <TextInput required type="number" value={price} onChange={(e) => setPrice(e.target.value)} className="w-32" />
      </Field>
      <Field label="Delivery period">
        <TextInput required placeholder="e.g. 14 days" value={period} onChange={(e) => setPeriod(e.target.value)} className="w-40" />
      </Field>
      <Field label="Quality certificate (optional)">
        <input
          type="file"
          onChange={(e) => setCert(e.target.files?.[0] ?? null)}
          className="block w-48 text-xs text-olive file:mr-2 file:border file:border-line file:bg-white file:px-2 file:py-1 file:text-xs"
        />
      </Field>
      <Button type="submit" disabled={busy}>{busy ? "Sending…" : "Submit offer"}</Button>
      {error && <p className="basis-full text-sm text-danger">{error}</p>}
    </form>
  );
}

function BrowseRFQs() {
  const [rfqs, setRfqs] = useState<RFQ[] | null>(null);

  const load = () => listRFQs({ status: "open" }).then((data) => setRfqs(unwrap(data)));
  useEffect(() => { load(); }, []);

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">Open RFQs</h1>
      {rfqs === null && <p className="mt-6 text-sm text-olive">Loading…</p>}
      {rfqs?.length === 0 && <div className="mt-6"><EmptyState title="No open RFQs right now" /></div>}
      <div className="mt-6 space-y-4">
        {rfqs?.map((rfq) => (
          <div key={rfq.id} className="border border-line bg-white p-4">
            <p className="text-sm font-medium text-ink">{rfq.commodity} — {rfq.quantity}{rfq.unit}</p>
            <p className="text-xs text-olive">
              {rfq.delivery_location} · by {rfq.delivery_date} · target {rfq.target_price} · {rfq.quality_verification_pref.replace(/_/g, " ")}
            </p>
            <div className="mt-3">
              <OfferForm rfq={rfq} onSubmitted={load} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["seller"]}>
      <BrowseRFQs />
    </RoleGuard>
  );
}
