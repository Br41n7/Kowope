"use client";

import { useEffect, useState, use as usePromise } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/Button";
import { Field, TextInput } from "@/components/Field";
import { useAuth } from "@/context/AuthContext";
import {
  addShipmentUpdate, createInspectionRequest, createLogisticsRequest,
  getOrder, listInspectionsForOrder, listLogisticsForOrder,
  submitInspectionReport, unwrap, updateOrderStatus,
} from "@/lib/endpoints";
import type { InspectionRequest, LogisticsRequest, PurchaseOrder } from "@/lib/types";
import { DocumentsPanel } from "@/components/DocumentsPanel";
import { ApiError } from "@/lib/api";

function LogisticsPanel({ orderId }: { orderId: number }) {
  const [requests, setRequests] = useState<LogisticsRequest[]>([]);
  const [pickup, setPickup] = useState("");
  const [delivery, setDelivery] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => listLogisticsForOrder(orderId).then((d) => setRequests(unwrap(d)));
  useEffect(() => { load(); }, [orderId]);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await createLogisticsRequest({ order: orderId, pickup_location: pickup, delivery_location: delivery });
      setPickup(""); setDelivery("");
      load();
    } finally {
      setBusy(false);
    }
  };

  const onUpdate = async (id: number, status: string) => {
    await addShipmentUpdate(id, { status });
    load();
  };

  return (
    <div className="border border-line bg-white p-4">
      <h3 className="font-mono text-sm uppercase tracking-wide text-olive">Logistics</h3>
      {requests.map((r) => (
        <div key={r.id} className="mt-3 border-t border-line pt-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink">{r.pickup_location} → {r.delivery_location}</p>
            <StatusBadge status={r.status} />
          </div>
          <div className="mt-2 flex gap-2">
            {["assigned", "in_transit", "delivered"].map((s) => (
              <Button key={s} variant="secondary" className="!py-1 !px-2 text-xs" onClick={() => onUpdate(r.id, s)}>
                Mark {s.replace("_", " ")}
              </Button>
            ))}
          </div>
          <ul className="mt-2 space-y-1 text-xs text-olive">
            {r.updates.map((u) => <li key={u.id}>{u.timestamp.slice(0, 16).replace("T", " ")} — {u.status}</li>)}
          </ul>
        </div>
      ))}
      <form onSubmit={onCreate} className="mt-4 flex flex-wrap items-end gap-2">
        <Field label="Pickup location">
          <TextInput required value={pickup} onChange={(e) => setPickup(e.target.value)} className="w-40" />
        </Field>
        <Field label="Delivery location">
          <TextInput required value={delivery} onChange={(e) => setDelivery(e.target.value)} className="w-40" />
        </Field>
        <Button type="submit" variant="secondary" disabled={busy}>Request logistics</Button>
      </form>
    </div>
  );
}

function InspectionPanel({ orderId }: { orderId: number }) {
  const [requests, setRequests] = useState<InspectionRequest[]>([]);
  const [findings, setFindings] = useState<Record<number, string>>({});
  const [certFile, setCertFile] = useState<Record<number, File | null>>({});
  const [photoFile, setPhotoFile] = useState<Record<number, File | null>>({});

  const load = () => listInspectionsForOrder(orderId).then((d) => setRequests(unwrap(d)));
  useEffect(() => { load(); }, [orderId]);

  const onCreate = async () => {
    await createInspectionRequest(orderId);
    load();
  };

  const onSubmitReport = async (id: number) => {
    await submitInspectionReport(id, findings[id] ?? "", {
      certificate: certFile[id] ?? null,
      photo: photoFile[id] ?? null,
    });
    load();
  };

  return (
    <div className="border border-line bg-white p-4">
      <h3 className="font-mono text-sm uppercase tracking-wide text-olive">Quality inspection</h3>
      {requests.map((r) => (
        <div key={r.id} className="mt-3 border-t border-line pt-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink">Inspection #{r.id}</p>
            <StatusBadge status={r.status} />
          </div>
          {r.report ? (
            <div className="mt-1">
              <p className="text-sm text-ink">{r.report.findings}</p>
              {r.report.certificate_file && (
                <a href={r.report.certificate_file} target="_blank" rel="noreferrer" className="text-xs text-ochre underline">
                  certificate
                </a>
              )}
              {r.report.photos?.map((p) => (
                <a key={p.id} href={p.image} target="_blank" rel="noreferrer" className="ml-2 text-xs text-ochre underline">
                  photo
                </a>
              ))}
            </div>
          ) : (
            <div className="mt-2 space-y-2">
              <input
                placeholder="Findings…"
                value={findings[r.id] ?? ""}
                onChange={(e) => setFindings({ ...findings, [r.id]: e.target.value })}
                className="w-full border border-line px-2 py-1 text-sm focus:border-ochre focus:outline-none"
              />
              <div className="flex flex-wrap items-center gap-2">
                <label className="text-xs text-olive">
                  Certificate:{" "}
                  <input
                    type="file"
                    onChange={(e) => setCertFile({ ...certFile, [r.id]: e.target.files?.[0] ?? null })}
                    className="text-xs file:mr-1 file:border file:border-line file:bg-white file:px-2 file:py-0.5 file:text-xs"
                  />
                </label>
                <label className="text-xs text-olive">
                  Photo:{" "}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setPhotoFile({ ...photoFile, [r.id]: e.target.files?.[0] ?? null })}
                    className="text-xs file:mr-1 file:border file:border-line file:bg-white file:px-2 file:py-0.5 file:text-xs"
                  />
                </label>
                <Button variant="secondary" className="!py-1 !px-2 text-xs" onClick={() => onSubmitReport(r.id)}>
                  Submit report
                </Button>
              </div>
            </div>
          )}
        </div>
      ))}
      <div className="mt-4">
        <Button variant="secondary" onClick={onCreate}>Request inspection</Button>
      </div>
    </div>
  );
}

function OrderDetail({ id }: { id: number }) {
  const { user } = useAuth();
  const [order, setOrder] = useState<PurchaseOrder | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => getOrder(id).then(setOrder);
  useEffect(() => { load(); }, [id]);

  const onStatus = async (status: string) => {
    setError(null);
    try {
      await updateOrderStatus(id, status);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? "That status change isn't allowed here." : "Update failed.");
    }
  };

  if (!order) return <p className="text-sm text-olive">Loading…</p>;

  const nextSteps: Record<string, string[]> = {
    issued: ["in_progress"],
    in_progress: ["delivered"],
    delivered: ["completed", "disputed"],
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-xl text-ink">{order.po_number}</h1>
        <StatusBadge status={order.status} />
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-olive">
        <div><dt className="inline">Commodity: </dt><dd className="inline text-ink">{order.terms_snapshot.commodity} ({order.terms_snapshot.grade || "—"})</dd></div>
        <div><dt className="inline">Quantity: </dt><dd className="inline text-ink">{order.terms_snapshot.quantity}{order.terms_snapshot.unit}</dd></div>
        <div><dt className="inline">Price: </dt><dd className="inline text-ink">{order.terms_snapshot.price}</dd></div>
        <div><dt className="inline">Delivery: </dt><dd className="inline text-ink">{order.terms_snapshot.delivery_location} by {order.terms_snapshot.delivery_date}</dd></div>
      </dl>

      {(nextSteps[order.status] ?? []).length > 0 && (
        <div className="mt-4 flex gap-2">
          {nextSteps[order.status].map((s) => (
            <Button key={s} variant="secondary" onClick={() => onStatus(s)}>
              Mark {s.replace("_", " ")}
            </Button>
          ))}
        </div>
      )}
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <LogisticsPanel orderId={order.id} />
        <InspectionPanel orderId={order.id} />
        <DocumentsPanel contentType="purchaseorder" objectId={order.id} />
      </div>

      <p className="mt-4 text-xs text-olive">Viewing as {user?.role} #{user?.id}</p>
    </div>
  );
}

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = usePromise(params);
  return (
    <RoleGuard allow={["buyer", "seller", "admin"]}>
      <OrderDetail id={Number(id)} />
    </RoleGuard>
  );
}
