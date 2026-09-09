"use client";

import { useEffect, useState } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { useAuth } from "@/context/AuthContext";
import { assignInspectionJob, listInspectionJobs, submitInspectionReport, unwrap } from "@/lib/endpoints";
import type { InspectionRequest } from "@/lib/types";
import { ApiError } from "@/lib/api";

function ReportForm({ requestId, onSubmitted }: { requestId: number; onSubmitted: () => void }) {
  const [findings, setFindings] = useState("");
  const [cert, setCert] = useState<File | null>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await submitInspectionReport(requestId, findings, { certificate: cert, photo });
      onSubmitted();
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="mt-2 space-y-2">
      <input
        required
        placeholder="Findings…"
        value={findings}
        onChange={(e) => setFindings(e.target.value)}
        className="w-full border border-line px-2 py-1 text-sm focus:border-ochre focus:outline-none"
      />
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-xs text-olive">
          Certificate:{" "}
          <input type="file" onChange={(e) => setCert(e.target.files?.[0] ?? null)}
            className="text-xs file:mr-1 file:border file:border-line file:bg-white file:px-2 file:py-0.5 file:text-xs" />
        </label>
        <label className="text-xs text-olive">
          Photo:{" "}
          <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
            className="text-xs file:mr-1 file:border file:border-line file:bg-white file:px-2 file:py-0.5 file:text-xs" />
        </label>
        <Button type="submit" variant="secondary" className="!py-1 !px-2 text-xs" disabled={busy}>
          {busy ? "Submitting…" : "Submit report"}
        </Button>
      </div>
    </form>
  );
}

function InspectorDashboard() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<InspectionRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => listInspectionJobs().then((data) => setJobs(unwrap(data)));
  useEffect(() => { load(); }, []);

  const onAssign = async (id: number) => {
    setError(null);
    try {
      await assignInspectionJob(id);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? "Could not claim this inspection — it may already be taken." : "Failed.");
    }
  };

  const pool = jobs?.filter((j) => j.status === "requested") ?? [];
  const mine = jobs?.filter((j) => j.inspector === user?.id) ?? [];

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">Inspector Desk</h1>
      <p className="mt-1 text-sm text-olive">Claim open inspection requests and submit findings with evidence.</p>

      <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">Open job pool</h2>
      {jobs === null && <p className="mt-3 text-sm text-olive">Loading…</p>}
      {jobs && pool.length === 0 && <div className="mt-3"><EmptyState title="No unclaimed inspections right now" /></div>}
      <div className="mt-3 divide-y divide-line border-t border-line">
        {pool.map((j) => (
          <div key={j.id} className="flex items-center justify-between py-3">
            <p className="text-sm font-medium text-ink">Inspection #{j.id} — Order #{j.order}</p>
            <Button className="!py-1 !px-2 text-xs" onClick={() => onAssign(j.id)}>Claim inspection</Button>
          </div>
        ))}
      </div>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">My assigned inspections</h2>
      {jobs && mine.length === 0 && <div className="mt-3"><EmptyState title="Nothing assigned to you yet" hint="Claim one from the pool above." /></div>}
      <div className="mt-3 space-y-3">
        {mine.map((j) => (
          <div key={j.id} className="border border-line bg-white p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-ink">Inspection #{j.id} — Order #{j.order}</p>
              <StatusBadge status={j.status} />
            </div>
            {j.report ? (
              <div className="mt-2">
                <p className="text-sm text-ink">{j.report.findings}</p>
                {j.report.certificate_file && (
                  <a href={j.report.certificate_file} target="_blank" rel="noreferrer" className="text-xs text-ochre underline">certificate</a>
                )}
                {j.report.photos?.map((p) => (
                  <a key={p.id} href={p.image} target="_blank" rel="noreferrer" className="ml-2 text-xs text-ochre underline">photo</a>
                ))}
              </div>
            ) : (
              <ReportForm requestId={j.id} onSubmitted={load} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["inspector"]}>
      <InspectorDashboard />
    </RoleGuard>
  );
}
