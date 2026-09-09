"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export function NavBar() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-line bg-parchment">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="font-mono text-sm tracking-tight text-ink">
          TradeAfric <span className="text-olive">/ desk</span>
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          {user?.role === "buyer" && (
            <>
              <Link href="/buyer/rfqs" className="hover:text-ochre">My RFQs</Link>
              <Link href="/buyer/rfqs/new" className="hover:text-ochre">Post RFQ</Link>
            </>
          )}
          {user?.role === "seller" && (
            <>
              <Link href="/seller/rfqs" className="hover:text-ochre">Browse RFQs</Link>
              <Link href="/seller/offers" className="hover:text-ochre">My Offers</Link>
            </>
          )}
          {user?.role === "logistics" && (
            <Link href="/logistics" className="hover:text-ochre">Logistics Desk</Link>
          )}
          {user?.role === "inspector" && (
            <Link href="/inspector" className="hover:text-ochre">Inspector Desk</Link>
          )}
          {user && (user.role === "buyer" || user.role === "seller" || user.role === "admin") && (
            <Link href="/orders" className="hover:text-ochre">Orders</Link>
          )}
          {user && <Link href="/notifications" className="hover:text-ochre">Notifications</Link>}
          {user?.role === "admin" && (
            <Link href="/admin/kyc-review" className="hover:text-ochre">KYC Review</Link>
          )}
          {user && !user.is_kyc_verified && (user.role === "buyer" || user.role === "seller") && (
            <Link href="/kyc" className="text-ochre">Complete KYC</Link>
          )}
          {user ? (
            <button onClick={logout} className="text-olive hover:text-danger">
              Sign out
            </button>
          ) : (
            <>
              <Link href="/login" className="hover:text-ochre">Log in</Link>
              <Link href="/register" className="hover:text-ochre">Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
