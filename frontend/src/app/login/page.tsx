"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Field, TextInput } from "@/components/Field";
import { Button } from "@/components/Button";
import { login } from "@/lib/endpoints";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { refresh } = useAuth();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      await refresh();
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? "Invalid username or password." : "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm">
      <h1 className="font-mono text-xl text-ink">Log in</h1>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <Field label="Username">
          <TextInput required value={username} onChange={(e) => setUsername(e.target.value)} />
        </Field>
        <Field label="Password">
          <TextInput type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        {error && <p className="text-sm text-danger">{error}</p>}
        <Button type="submit" disabled={loading}>{loading ? "Logging in…" : "Log in"}</Button>
      </form>
    </div>
  );
}
