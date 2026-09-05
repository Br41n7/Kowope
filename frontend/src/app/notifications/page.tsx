"use client";

import { useEffect, useState } from "react";
import { EmptyState } from "@/components/EmptyState";
import { listNotifications, markNotificationRead, unwrap } from "@/lib/endpoints";
import type { AppNotification } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function NotificationsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [notifications, setNotifications] = useState<AppNotification[] | null>(null);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  const load = () => listNotifications().then((data) => setNotifications(unwrap(data)));
  useEffect(() => {
    if (user) load();
  }, [user]);

  const onRead = async (id: number) => {
    await markNotificationRead(id);
    load();
  };

  if (loading || !user) return <p className="text-sm text-olive">Loading…</p>;

  return (
    <div>
      <h1 className="font-mono text-xl text-ink">Notifications</h1>
      {notifications?.length === 0 && <div className="mt-6"><EmptyState title="You're all caught up" /></div>}
      <div className="mt-6 divide-y divide-line border-t border-line">
        {notifications?.map((n) => (
          <button
            key={n.id}
            onClick={() => !n.is_read && onRead(n.id)}
            className={`block w-full py-3 text-left ${n.is_read ? "text-olive" : "text-ink font-medium"}`}
          >
            {n.message}
            <span className="ml-2 text-xs text-olive">{n.created_at.slice(0, 16).replace("T", " ")}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
