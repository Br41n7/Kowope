"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { listRFQs, unwrap } from "@/lib/endpoints";
import type { RFQ } from "@/lib/types";

function BuyerRFQList() {
  const [rfqs, setRfqs] = useState<RFQ[] | null>(null);

  useEffect(() => {
    listRFQs().then((data) => setRfqs(unwrap(data)));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-xl text-ink">My RFQs</h1>
        <Link href="/buyer/rfqs/new" className="bg-ochre px-3 py-1.5 text-sm font-medium text-white hover:bg-ochre/90">
          Post RFQ
        </Link>
      </div>

      {rfqs === null && <p className="mt-6 text-sm text-olive">Loading…</p>}
      {rfqs?.length === 0 && (
        <div className="mt-6">
          <EmptyState title="No RFQs yet" hint="Post one to start receiving offers from sellers." />
        </div>
      )}

      <div className="mt-6 divide-y divide-line border-t border-line">
        {rfqs?.map((rfq) => (
          <Link
            key={rfq.id}
            href={`/buyer/rfqs/${rfq.id}`}
            className="flex items-center justify-between gap-4 py-3 hover:bg-ink/5"
          >
            <div>
              <p className="text-sm font-medium text-ink">{rfq.commodity} — {rfq.quantity}{rfq.unit}</p>
              <p className="text-xs text-olive">{rfq.delivery_location} · by {rfq.delivery_date}</p>
            </div>
            <StatusBadge status={rfq.status} />
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["buyer"]}>
      <BuyerRFQList />
    </RoleGuard>
  );
}
