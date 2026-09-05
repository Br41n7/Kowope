"use client";

import { useEffect, useState } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/Button";
import { listKYCReviews, reviewKYC, unwrap } from "@/lib/endpoints";
import type { KYCProfile } from "@/lib/types";

function KYCReview() {
  const [profiles, setProfiles] = useState<KYCProfile[] | null>(null);

  const load = () => listKYCReviews().then((data) => setProfiles(unwrap(data)));
  useEffect(() => { load(); }, []);

  const onReview = async (id: number, status: "approved" | "rejected") => {
    await reviewKYC(id, status);
    load();
  };

  const pending = profiles?.filter((p) => p.status === "pending") ?? [];
  const decided = profiles?.filter((p) => p.status !== "pending") ?? [];

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">KYC Review</h1>

      <h2 className="mt-6 font-mono text-sm uppercase tracking-wide text-olive">Pending</h2>
      {profiles === null && <p className="mt-3 text-sm text-olive">Loading…</p>}
      {profiles && pending.length === 0 && <div className="mt-3"><EmptyState title="Nothing pending" /></div>}
      <div className="mt-3 divide-y divide-line border-t border-line">
        {pending.map((p) => (
          <div key={p.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">{p.business_name}</p>
              <p className="text-xs text-olive">{p.user.username} · {p.user.role} · reg. {p.registration_number || "—"}</p>
            </div>
            <div className="flex gap-2">
              <Button className="!py-1 !px-2 text-xs" onClick={() => onReview(p.id, "approved")}>Approve</Button>
              <Button variant="danger" className="!py-1 !px-2 text-xs" onClick={() => onReview(p.id, "rejected")}>Reject</Button>
            </div>
          </div>
        ))}
      </div>

      {decided.length > 0 && (
        <>
          <h2 className="mt-8 font-mono text-sm uppercase tracking-wide text-olive">Reviewed</h2>
          <div className="mt-3 divide-y divide-line border-t border-line">
            {decided.map((p) => (
              <div key={p.id} className="flex items-center justify-between py-3">
                <p className="text-sm text-ink">{p.business_name} — {p.user.username}</p>
                <StatusBadge status={p.status} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["admin"]}>
      <KYCReview />
    </RoleGuard>
  );
}
