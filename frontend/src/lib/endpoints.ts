import { apiFetch, setTokens } from "./api";
import type {
  AppNotification, Document, InspectionRequest, KYCProfile, LogisticsRequest,
  NegotiationMessage, Offer, PurchaseOrder, RFQ, ShipmentUpdate, User,
} from "./types";

// ---- Auth ----
export async function register(payload: {
  username: string; email: string; password: string; role: string; phone?: string;
}) {
  const data = await apiFetch<{ user: User; access: string; refresh: string }>("/auth/register/", {
    method: "POST", body: payload, auth: false,
  });
  setTokens(data.access, data.refresh);
  return data.user;
}

export async function login(username: string, password: string) {
  const data = await apiFetch<{ access: string; refresh: string }>("/auth/login/", {
    method: "POST", body: { username, password }, auth: false,
  });
  setTokens(data.access, data.refresh);
  return fetchMe();
}

export function fetchMe() {
  return apiFetch<User>("/auth/me/");
}

// ---- KYC ----
export function submitKYC(payload: { business_name: string; registration_number?: string; tax_id?: string; address?: string }) {
  return apiFetch<KYCProfile>("/kyc/submit/", { method: "POST", body: payload });
}

export function listKYCReviews() {
  return apiFetch<{ results: KYCProfile[] } | KYCProfile[]>("/kyc-review/");
}

export function reviewKYC(id: number, status: "approved" | "rejected") {
  return apiFetch<KYCProfile>(`/kyc-review/${id}/`, { method: "PATCH", body: { status } });
}

// ---- Marketplace ----
export function listRFQs(params?: Record<string, string>) {
  const qs = params ? `?${new URLSearchParams(params)}` : "";
  return apiFetch<{ results: RFQ[] } | RFQ[]>(`/rfqs/${qs}`);
}

export function getRFQ(id: number) {
  return apiFetch<RFQ>(`/rfqs/${id}/`);
}

export function createRFQ(payload: Omit<RFQ, "id" | "buyer" | "status" | "created_at">) {
  return apiFetch<RFQ>("/rfqs/", { method: "POST", body: payload });
}

export function listOffersForRFQ(rfqId: number) {
  return apiFetch<{ results: Offer[] } | Offer[]>(`/offers/?rfq=${rfqId}`);
}

export function createOffer(payload: { rfq: number; price: string; delivery_period: string; quality_certs?: File | null }) {
  if (payload.quality_certs) {
    const fd = new FormData();
    fd.append("rfq", String(payload.rfq));
    fd.append("price", payload.price);
    fd.append("delivery_period", payload.delivery_period);
    fd.append("quality_certs", payload.quality_certs);
    return apiFetch<Offer>("/offers/", { method: "POST", body: fd, isFormData: true });
  }
  return apiFetch<Offer>("/offers/", { method: "POST", body: { rfq: payload.rfq, price: payload.price, delivery_period: payload.delivery_period } });
}

export function acceptOffer(offerId: number) {
  return apiFetch<PurchaseOrder>(`/offers/${offerId}/accept/`, { method: "POST" });
}

export function rejectOffer(offerId: number) {
  return apiFetch<Offer>(`/offers/${offerId}/reject/`, { method: "POST" });
}

export function listMessages(offerId: number) {
  return apiFetch<NegotiationMessage[]>(`/offers/${offerId}/messages/`);
}

export function sendMessage(offerId: number, message: string, attachment?: File | null) {
  if (attachment) {
    const fd = new FormData();
    fd.append("message", message);
    fd.append("attachment", attachment);
    return apiFetch<NegotiationMessage>(`/offers/${offerId}/messages/`, { method: "POST", body: fd, isFormData: true });
  }
  return apiFetch<NegotiationMessage>(`/offers/${offerId}/messages/`, { method: "POST", body: { message } });
}

// ---- Orders ----
export function listOrders(params?: Record<string, string>) {
  const qs = params ? `?${new URLSearchParams(params)}` : "";
  return apiFetch<{ results: PurchaseOrder[] } | PurchaseOrder[]>(`/orders/${qs}`);
}

export function getOrder(id: number) {
  return apiFetch<PurchaseOrder>(`/orders/${id}/`);
}

export function updateOrderStatus(id: number, status: string) {
  return apiFetch<PurchaseOrder>(`/orders/${id}/`, { method: "PATCH", body: { status } });
}

// ---- Logistics ----
export function createLogisticsRequest(payload: { order: number; pickup_location: string; delivery_location: string }) {
  return apiFetch<LogisticsRequest>("/logistics-requests/", { method: "POST", body: payload });
}

export function listLogisticsForOrder(orderId: number) {
  return apiFetch<{ results: LogisticsRequest[] } | LogisticsRequest[]>(`/logistics-requests/?order=${orderId}`);
}

export function addShipmentUpdate(requestId: number, payload: { status: string; note?: string }) {
  return apiFetch<ShipmentUpdate>(`/logistics-requests/${requestId}/updates/`, { method: "POST", body: payload });
}

// ---- Quality ----
export function createInspectionRequest(orderId: number) {
  return apiFetch<InspectionRequest>("/inspection-requests/", { method: "POST", body: { order: orderId } });
}

export function listInspectionsForOrder(orderId: number) {
  return apiFetch<{ results: InspectionRequest[] } | InspectionRequest[]>(`/inspection-requests/?order=${orderId}`);
}

export function submitInspectionReport(
  requestId: number,
  findings: string,
  files?: { certificate?: File | null; photo?: File | null; photoCaption?: string }
) {
  if (files?.certificate || files?.photo) {
    const fd = new FormData();
    fd.append("findings", findings);
    if (files.certificate) fd.append("certificate_file", files.certificate);
    if (files.photo) {
      fd.append("photos[0]image", files.photo);
      fd.append("photos[0]caption", files.photoCaption ?? "");
    }
    return apiFetch(`/inspection-requests/${requestId}/report/`, { method: "POST", body: fd, isFormData: true });
  }
  return apiFetch(`/inspection-requests/${requestId}/report/`, { method: "POST", body: { findings } });
}

// ---- Documents ----
export function listDocuments(contentType: string, objectId: number) {
  return apiFetch<{ results: Document[] } | Document[]>(`/documents/?content_type=${contentType}&object_id=${objectId}`);
}

export function uploadDocument(payload: { content_type: string; object_id: number; doc_type: string; file: File }) {
  const fd = new FormData();
  fd.append("content_type", payload.content_type);
  fd.append("object_id", String(payload.object_id));
  fd.append("doc_type", payload.doc_type);
  fd.append("file", payload.file);
  return apiFetch<Document>("/documents/", { method: "POST", body: fd, isFormData: true });
}

// ---- Notifications ----
export function listNotifications() {
  return apiFetch<{ results: AppNotification[] } | AppNotification[]>("/notifications/");
}

export function markNotificationRead(id: number) {
  return apiFetch<AppNotification>(`/notifications/${id}/`, { method: "PATCH", body: { is_read: true } });
}

// Helper: DRF pagination may or may not be wrapped depending on PAGE_SIZE settings — normalize.
export function unwrap<T>(data: { results: T[] } | T[]): T[] {
  return Array.isArray(data) ? data : data.results;
}
