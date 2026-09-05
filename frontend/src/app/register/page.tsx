"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Field, TextInput, Select } from "@/components/Field";
import { Button } from "@/components/Button";
import { register } from "@/lib/endpoints";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "", role: "buyer" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { refresh } = useAuth();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form);
      await refresh();
      router.push("/kyc");
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.body) : "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm">
      <h1 className="font-mono text-xl text-ink">Create an account</h1>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <Field label="Username">
          <TextInput required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </Field>
        <Field label="Email">
          <TextInput type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </Field>
        <Field label="Password">
          <TextInput type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </Field>
        <Field label="I am a">
          <Select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="buyer">Buyer</option>
            <option value="seller">Seller</option>
          </Select>
        </Field>
        {error && <p className="text-sm text-danger">{error}</p>}
        <Button type="submit" disabled={loading}>{loading ? "Creating…" : "Create account"}</Button>
      </form>
    </div>
  );
}
