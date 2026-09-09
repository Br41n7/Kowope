// Same-origin relative path — the browser always talks to its own origin, and
// Next.js proxies /api/* to the Django backend server-side (see next.config.ts).
// This is what makes httpOnly cookie auth work with zero CORS configuration.
const API_BASE = "/api/v1";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(typeof body === "string" ? body : JSON.stringify(body));
    this.status = status;
    this.body = body;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  isFormData?: boolean;
  auth?: boolean;
}

async function refreshAccessToken(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    credentials: "include",
  });
  return res.ok;
}

export async function apiFetch<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, isFormData = false } = opts;

  const doFetch = (): Promise<Response> => {
    const headers: Record<string, string> = {};
    if (!isFormData) headers["Content-Type"] = "application/json";

    return fetch(`${API_BASE}${path}`, {
      method,
      headers,
      credentials: "include", // send/receive the httpOnly auth cookies
      body: body ? (isFormData ? (body as FormData) : JSON.stringify(body)) : undefined,
    });
  };

  let res = await doFetch();

  // Access-token cookie expired — the refresh cookie (longer-lived) can silently mint
  // a new one server-side. Retry exactly once after a successful refresh.
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) res = await doFetch();
  }

  if (!res.ok) {
    let errBody: unknown;
    try {
      errBody = await res.json();
    } catch {
      errBody = await res.text();
    }
    throw new ApiError(res.status, errBody);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}
