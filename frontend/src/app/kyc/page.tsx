"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Field, TextInput } from "@/components/Field";
import { Button } from "@/components/Button";
import { submitKYC } from "@/lib/endpoints";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/lib/api";

export default function KYCPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ business_name: "", registration_number: "", tax_id: "", address: "" });
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [busy, setBusy] = useState(false);

  if (loading) return <p className="text-sm text-olive">Loading…</p>;
  if (!user) {
    router.replace("/login");
    return null;
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await submitKYC(form);
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.body) : "Submission failed.");
    } finally {
      setBusy(false);
    }
  };

  if (user.is_kyc_verified) {
    return <p className="text-sm text-success">Your KYC is already approved.</p>;
  }

  if (submitted) {
    return (
      <div className="max-w-md border border-line bg-white p-6">
        <p className="text-sm text-ink">
          Your KYC details were submitted and are pending admin review. You&apos;ll be able to
          post RFQs or offers once approved.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-sm">
      <h1 className="font-mono text-xl text-ink">Submit KYC</h1>
      <p className="mt-1 text-sm text-olive">Required before you can trade on the platform.</p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <Field label="Business name">
          <TextInput required value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} />
        </Field>
        <Field label="Registration number">
          <TextInput value={form.registration_number} onChange={(e) => setForm({ ...form, registration_number: e.target.value })} />
        </Field>
        <Field label="Tax ID">
          <TextInput value={form.tax_id} onChange={(e) => setForm({ ...form, tax_id: e.target.value })} />
        </Field>
        <Field label="Business address">
          <TextInput value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        </Field>
        {error && <p className="text-sm text-danger">{error}</p>}
        <Button type="submit" disabled={busy}>{busy ? "Submitting…" : "Submit for review"}</Button>
      </form>
    </div>
  );
}
