"use client";

import { useEffect, useState } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { useAuth } from "@/context/AuthContext";
import { addShipmentUpdate, assignLogisticsJob, listLogisticsJobs, unwrap } from "@/lib/endpoints";
import type { LogisticsRequest } from "@/lib/types";
import { ApiError } from "@/lib/api";

const NEXT_STATUS: Record<string, string[]> = {
  assigned: ["in_transit"],
  in_transit: ["delivered"],
};

function LogisticsDashboard() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<LogisticsRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => listLogisticsJobs().then((data) => setJobs(unwrap(data)));
  useEffect(() => { load(); }, []);

  const onAssign = async (id: number) => {
    setError(null);
    try {
      await assignLogisticsJob(id);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? "Could not claim this job — it may already be taken." : "Failed.");
    }
  };

  const onUpdate = async (id: number, status: string) => {
    await addShipmentUpdate(id, { status });
    load();
  };

  const pool = jobs?.filter((j) => j.status === "requested") ?? [];
  const mine = jobs?.filter((j) => j.assigned_partner === user?.id) ?? [];

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">Logistics Desk</h1>
      <p className="mt-1 text-sm text-olive">Claim open haulage requests and track your assigned shipments.</p>

      <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">Open job pool</h2>
      {jobs === null && <p className="mt-3 text-sm text-olive">Loading…</p>}
      {jobs && pool.length === 0 && <div className="mt-3"><EmptyState title="No unclaimed jobs right now" /></div>}
      <div className="mt-3 divide-y divide-line border-t border-line">
        {pool.map((j) => (
          <div key={j.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">Order #{j.order}</p>
              <p className="text-xs text-olive">{j.pickup_location} → {j.delivery_location}</p>
            </div>
            <Button className="!py-1 !px-2 text-xs" onClick={() => onAssign(j.id)}>Claim job</Button>
          </div>
        ))}
      </div>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">My assigned shipments</h2>
      {jobs && mine.length === 0 && <div className="mt-3"><EmptyState title="Nothing assigned to you yet" hint="Claim a job from the pool above." /></div>}
      <div className="mt-3 space-y-3">
        {mine.map((j) => (
          <div key={j.id} className="border border-line bg-white p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-ink">Order #{j.order} — {j.pickup_location} → {j.delivery_location}</p>
              <StatusBadge status={j.status} />
            </div>
            {(NEXT_STATUS[j.status] ?? []).length > 0 && (
              <div className="mt-2 flex gap-2">
                {NEXT_STATUS[j.status].map((s) => (
                  <Button key={s} variant="secondary" className="!py-1 !px-2 text-xs" onClick={() => onUpdate(j.id, s)}>
                    Mark {s.replace("_", " ")}
                  </Button>
                ))}
              </div>
            )}
            <ul className="mt-2 space-y-1 text-xs text-olive">
              {j.updates.map((u) => <li key={u.id}>{u.timestamp.slice(0, 16).replace("T", " ")} — {u.status}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["logistics"]}>
      <LogisticsDashboard />
    </RoleGuard>
  );
}
