"use client";

import { useEffect, useState } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { useAuth } from "@/context/AuthContext";
import { listOffers, unwrap } from "@/lib/endpoints";
import type { Offer } from "@/lib/types";

function MyOffers() {
  const { user } = useAuth();
  const [offers, setOffers] = useState<Offer[] | null>(null);

  useEffect(() => {
    if (!user) return;
    listOffers({ seller: String(user.id) }).then((data) => setOffers(unwrap(data)));
  }, [user]);

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">My Offers</h1>
      {offers === null && <p className="mt-6 text-sm text-olive">Loading…</p>}
      {offers?.length === 0 && <div className="mt-6"><EmptyState title="You haven't made any offers yet" /></div>}
      <div className="mt-6 divide-y divide-line border-t border-line">
        {offers?.map((offer) => (
          <div key={offer.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">Offer #{offer.id} on RFQ #{offer.rfq}</p>
              <p className="text-xs text-olive">{offer.price} · {offer.delivery_period}</p>
            </div>
            <StatusBadge status={offer.status} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["seller"]}>
      <MyOffers />
    </RoleGuard>
  );
}
