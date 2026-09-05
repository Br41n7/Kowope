"use client";

import { useEffect, useState, use as usePromise } from "react";
import { useRouter } from "next/navigation";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { acceptOffer, getRFQ, listOffersForRFQ, listMessages, rejectOffer, sendMessage, unwrap } from "@/lib/endpoints";
import type { NegotiationMessage, Offer, RFQ } from "@/lib/types";
import { ApiError } from "@/lib/api";

function OfferThread({ offer, onChanged }: { offer: Offer; onChanged: () => void }) {
  const [messages, setMessages] = useState<NegotiationMessage[]>(offer.messages ?? []);
  const [text, setText] = useState("");
  const [attachment, setAttachment] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshMessages = () => listMessages(offer.id).then(setMessages);

  const onAccept = async () => {
    setBusy(true);
    setError(null);
    try {
      await acceptOffer(offer.id);
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.body) : "Could not accept offer.");
    } finally {
      setBusy(false);
    }
  };

  const onReject = async () => {
    setBusy(true);
    try {
      await rejectOffer(offer.id);
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  const onSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() && !attachment) return;
    await sendMessage(offer.id, text, attachment);
    setText("");
    setAttachment(null);
    refreshMessages();
  };

  return (
    <div className="border border-line bg-white p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-ink">Offer #{offer.id} — {offer.price} · {offer.delivery_period}</p>
          {offer.quality_certs && (
            <a href={offer.quality_certs} target="_blank" rel="noreferrer" className="text-xs text-ochre underline">
              View quality certificate
            </a>
          )}
        </div>
        <StatusBadge status={offer.status} />
      </div>

      {(offer.status === "submitted" || offer.status === "countered") && (
        <div className="mt-3 flex gap-2">
          <Button onClick={onAccept} disabled={busy}>Accept &amp; issue PO</Button>
          <Button variant="secondary" onClick={onReject} disabled={busy}>Reject</Button>
        </div>
      )}
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <div className="mt-4 space-y-2 border-t border-line pt-3">
        {messages.length === 0 && <p className="text-xs text-olive">No messages yet.</p>}
        {messages.map((m) => (
          <p key={m.id} className="text-sm text-ink">
            <span className="text-olive">#{m.sender}:</span> {m.message}
            {m.attachment && (
              <a href={m.attachment} target="_blank" rel="noreferrer" className="ml-2 text-xs text-ochre underline">
                attachment
              </a>
            )}
          </p>
        ))}
      </div>
      <form onSubmit={onSend} className="mt-3 flex flex-wrap items-center gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Send a counter-offer note…"
          className="flex-1 border border-line px-3 py-1.5 text-sm focus:border-ochre focus:outline-none"
        />
        <input
          type="file"
          onChange={(e) => setAttachment(e.target.files?.[0] ?? null)}
          className="w-40 text-xs text-olive file:mr-2 file:border file:border-line file:bg-white file:px-2 file:py-1 file:text-xs"
        />
        <Button type="submit" variant="secondary">Send</Button>
      </form>
    </div>
  );
}

function RFQDetail({ id }: { id: number }) {
  const router = useRouter();
  const [rfq, setRfq] = useState<RFQ | null>(null);
  const [offers, setOffers] = useState<Offer[]>([]);

  const load = () => {
    getRFQ(id).then(setRfq);
    listOffersForRFQ(id).then((data) => setOffers(unwrap(data)));
  };

  useEffect(load, [id]);

  const onOfferChanged = () => {
    load();
  };

  if (!rfq) return <p className="text-sm text-olive">Loading…</p>;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-xl text-ink">{rfq.commodity} — {rfq.quantity}{rfq.unit}</h1>
        <StatusBadge status={rfq.status} />
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-olive">
        <div><dt className="inline">Delivery: </dt><dd className="inline text-ink">{rfq.delivery_location}, by {rfq.delivery_date}</dd></div>
        <div><dt className="inline">Target price: </dt><dd className="inline text-ink">{rfq.target_price}</dd></div>
        <div><dt className="inline">Quality check: </dt><dd className="inline text-ink">{rfq.quality_verification_pref.replace(/_/g, " ")}</dd></div>
        <div><dt className="inline">Payment: </dt><dd className="inline text-ink">{rfq.payment_pref}</dd></div>
      </dl>

      <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">Offers</h2>
      {offers.length === 0 && (
        <div className="mt-3">
          <EmptyState title="No offers yet" hint="Sellers browsing the marketplace will see this RFQ if it's open." />
        </div>
      )}
      <div className="mt-3 space-y-3">
        {offers.map((offer) => (
          <OfferThread key={offer.id} offer={offer} onChanged={onOfferChanged} />
        ))}
      </div>

      {rfq.status === "closed" && (
        <p className="mt-6 text-sm text-success">
          This RFQ is closed — check <button className="underline" onClick={() => router.push("/orders")}>your orders</button> for the resulting purchase order.
        </p>
      )}
    </div>
  );
}

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = usePromise(params);
  return (
    <RoleGuard allow={["buyer"]}>
      <RFQDetail id={Number(id)} />
    </RoleGuard>
  );
}
