"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import type { Role } from "@/lib/types";

export function RoleGuard({ allow, children }: { allow: Role[]; children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
    if (!loading && user && !allow.includes(user.role)) router.replace("/");
  }, [loading, user, allow, router]);

  if (loading || !user || !allow.includes(user.role)) {
    return <div className="p-8 text-sm text-olive">Checking access…</div>;
  }
  return <>{children}</>;
}
