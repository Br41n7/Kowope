"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RoleGuard } from "@/components/RoleGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { listOrders, unwrap } from "@/lib/endpoints";
import type { PurchaseOrder } from "@/lib/types";

function OrdersList() {
  const [orders, setOrders] = useState<PurchaseOrder[] | null>(null);

  useEffect(() => {
    listOrders().then((data) => setOrders(unwrap(data)));
  }, []);

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">Orders</h1>
      {orders === null && <p className="mt-6 text-sm text-olive">Loading…</p>}
      {orders?.length === 0 && <div className="mt-6"><EmptyState title="No purchase orders yet" hint="These are created automatically when a buyer accepts an offer." /></div>}
      <div className="mt-6 divide-y divide-line border-t border-line">
        {orders?.map((order) => (
          <Link key={order.id} href={`/orders/${order.id}`} className="flex items-center justify-between py-3 hover:bg-ink/5">
            <div>
              <p className="font-mono text-sm text-ink">{order.po_number}</p>
              <p className="text-xs text-olive">{order.terms_snapshot.commodity} — {order.terms_snapshot.quantity}{order.terms_snapshot.unit}</p>
            </div>
            <StatusBadge status={order.status} />
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGuard allow={["buyer", "seller", "admin"]}>
      <OrdersList />
    </RoleGuard>
  );
}
