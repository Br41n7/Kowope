"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { RoleGuard } from "@/components/RoleGuard";
import { Field, TextInput, Select } from "@/components/Field";
import { Button } from "@/components/Button";
import { createRFQ } from "@/lib/endpoints";
import { ApiError } from "@/lib/api";

function NewRFQForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    commodity: "", grade: "", quantity: "", unit: "MT",
    delivery_location: "", delivery_date: "", target_price: "",
    quality_verification_pref: "sample", payment_pref: "escrow",
  });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const rfq = await createRFQ(form as never);
      router.push(`/buyer/rfqs/${rfq.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.body) : "Could not create RFQ.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-md">
      <h1 className="font-mono text-xl text-ink">Post a new RFQ</h1>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <Field label="Commodity">
          <TextInput required value={form.commodity} onChange={(e) => setForm({ ...form, commodity: e.target.value })} />
        </Field>
        <Field label="Grade">
          <TextInput value={form.grade} onChange={(e) => setForm({ ...form, grade: e.target.value })} />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Quantity">
            <TextInput required type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
          </Field>
          <Field label="Unit">
            <TextInput required value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
          </Field>
        </div>
        <Field label="Delivery location">
          <TextInput required value={form.delivery_location} onChange={(e) => setForm({ ...form, delivery_location: e.target.value })} />
        </Field>
        <Field label="Delivery date">
          <TextInput required type="date" value={form.delivery_date} onChange={(e) => setForm({ ...form, delivery_date: e.target.value })} />
        </Field>
        <Field label="Target price">
          <TextInput required type="number" value={form.target_price} onChange={(e) => setForm({ ...form, target_price: e.target.value })} />
        </Field>
        <Field label="Quality verification">
          <Select value={form.quality_verification_pref} onChange={(e) => setForm({ ...form, quality_verification_pref: e.target.value })}>
            <option value="delivery_test">Test on delivery</option>
            <option value="independent">Independent verification</option>
            <option value="sample">Sample testing</option>
          </Select>
        </Field>
        <Field label="Payment preference">
          <Select value={form.payment_pref} onChange={(e) => setForm({ ...form, payment_pref: e.target.value })}>
            <option value="escrow">Escrow</option>
            <option value="guarantee">Bank guarantee</option>
            <option value="credit">Credit sale</option>
          </Select>
        </Field>
        {error && <p className="text-sm text-danger">{error}</p>}
        <Button type="submit" disabled={busy}>{busy ? "Posting…" : "Post RFQ"}</Button>
      </form>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["buyer"]}>
      <NewRFQForm />
    </RoleGuard>
  );
}
