"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="max-w-xl">
      <h1 className="font-mono text-2xl text-ink">TradeAfric Trade Desk</h1>
      <p className="mt-3 text-sm leading-relaxed text-olive">
        Post requests for quality-graded commodities, negotiate offers, and move a trade
        from request to purchase order to delivery — with an inspection and logistics
        trail attached at every step.
      </p>

      {!user && (
        <div className="mt-6 flex gap-3">
          <Link href="/register" className="bg-ochre px-4 py-2 text-sm font-medium text-white hover:bg-ochre/90">
            Create an account
          </Link>
          <Link href="/login" className="border border-ink/30 px-4 py-2 text-sm font-medium text-ink hover:bg-ink/5">
            Log in
          </Link>
        </div>
      )}

      {user && !user.is_kyc_verified && (user.role === "buyer" || user.role === "seller") && (
        <div className="mt-6 border border-ochre/40 bg-ochre/10 px-4 py-3 text-sm text-ink">
          Your KYC is not yet approved. <Link href="/kyc" className="underline">Submit your business details</Link> to
          start posting RFQs or offers.
        </div>
      )}

      {user && user.is_kyc_verified && user.role === "buyer" && (
        <Link href="/buyer/rfqs/new" className="mt-6 inline-block bg-ochre px-4 py-2 text-sm font-medium text-white hover:bg-ochre/90">
          Post a new RFQ
        </Link>
      )}
      {user && user.is_kyc_verified && user.role === "seller" && (
        <Link href="/seller/rfqs" className="mt-6 inline-block bg-ochre px-4 py-2 text-sm font-medium text-white hover:bg-ochre/90">
          Browse open RFQs
        </Link>
      )}
      {user && user.role === "logistics" && (
        <Link href="/logistics" className="mt-6 inline-block bg-ochre px-4 py-2 text-sm font-medium text-white hover:bg-ochre/90">
          Open the Logistics Desk
        </Link>
      )}
      {user && user.role === "inspector" && (
        <Link href="/inspector" className="mt-6 inline-block bg-ochre px-4 py-2 text-sm font-medium text-white hover:bg-ochre/90">
          Open the Inspector Desk
        </Link>
      )}
    </div>
  );
}
