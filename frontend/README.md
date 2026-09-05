# TradeAfric Frontend (MVP)

Next.js (App Router, TypeScript, Tailwind v4) frontend for the TradeAfric MVP, consuming the Django backend in `../backend`.

## Setup

```bash
npm install
cp .env.example .env.local     # set NEXT_PUBLIC_API_BASE_URL if your backend isn't on localhost:8000
npm run dev
```
Open http://localhost:3000. The Django backend must be running on the URL in `.env.local` (CORS is already configured on the backend for `http://localhost:3000`).

## Pages implemented (mirrors the MVP scope)
- `/register`, `/login`, `/kyc` — auth + KYC submission
- `/buyer/rfqs`, `/buyer/rfqs/new`, `/buyer/rfqs/[id]` — buyer RFQ management, offers, negotiation, accept/reject
- `/seller/rfqs`, `/seller/offers` — seller marketplace browsing + offer submission
- `/orders`, `/orders/[id]` — purchase order detail, status transitions, logistics panel, inspection panel
- `/admin/kyc-review` — admin KYC approval queue
- `/notifications` — in-app notifications

## Auth
JWT access/refresh tokens are stored in `localStorage` and attached via `src/lib/api.ts`, which
transparently refreshes an expired access token on a 401 and retries once. For a production
deployment, consider moving to httpOnly cookies via a Next.js API route proxy instead —
localStorage is simple but vulnerable to XSS reading the token.

## Design tokens
See `src/app/globals.css` — deep bottle-green ink (`#12261E`) on parchment (`#F7F4EC`), burnt-ochre
accent (`#C4741F`) for primary actions, IBM Plex Sans/Mono (falls back to system fonts if Google
Fonts isn't reachable in your environment — see `next/font/google` in `layout.tsx` if you want to
restore webfont loading).

## Type safety
`src/lib/types.ts` mirrors the Django serializers field-for-field. If you change a backend
serializer, update the matching type here.

## Not yet built (v2/v3, matches backend scope)
Escrow/FX/wallet UI, financier marketplace, insurance marketplace, live GPS map view,
AI risk scoring displays — see `../tradeafric_mvp_plan.md`.
