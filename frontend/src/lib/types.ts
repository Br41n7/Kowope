export type Role = "buyer" | "seller" | "admin" | "logistics" | "inspector";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  phone: string;
  is_kyc_verified: boolean;
}

export type KYCStatus = "pending" | "approved" | "rejected";

export interface KYCProfile {
  id: number;
  user: User;
  business_name: string;
  registration_number: string;
  tax_id: string;
  address: string;
  status: KYCStatus;
  reviewed_by: number | null;
  reviewed_at: string | null;
  created_at: string;
}

export type RFQStatus = "open" | "closed" | "cancelled";
export type QualityPref = "delivery_test" | "independent" | "sample";
export type PaymentPref = "escrow" | "guarantee" | "credit";

export interface RFQ {
  id: number;
  buyer: number;
  commodity: string;
  grade: string;
  quantity: string;
  unit: string;
  delivery_location: string;
  delivery_date: string;
  target_price: string;
  quality_verification_pref: QualityPref;
  payment_pref: PaymentPref;
  status: RFQStatus;
  created_at: string;
}

export type OfferStatus = "submitted" | "countered" | "accepted" | "rejected";

export interface NegotiationMessage {
  id: number;
  offer: number;
  sender: number;
  message: string;
  attachment: string | null;
  created_at: string;
}

export interface Offer {
  id: number;
  rfq: number;
  seller: number;
  price: string;
  delivery_period: string;
  quality_certs: string | null;
  status: OfferStatus;
  created_at: string;
  messages: NegotiationMessage[];
}

export type OrderStatus =
  | "issued" | "in_progress" | "delivered" | "disputed" | "completed" | "cancelled";

export interface PurchaseOrder {
  id: number;
  offer: number;
  buyer: number;
  seller: number;
  po_number: string;
  terms_snapshot: Record<string, string>;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
}

export type LogisticsStatus = "requested" | "assigned" | "in_transit" | "delivered";

export interface ShipmentUpdate {
  id: number;
  request: number;
  status: LogisticsStatus;
  note: string;
  timestamp: string;
}

export interface LogisticsRequest {
  id: number;
  order: number;
  pickup_location: string;
  delivery_location: string;
  status: LogisticsStatus;
  assigned_partner: number | null;
  created_at: string;
  updates: ShipmentUpdate[];
}

export type InspectionStatus = "requested" | "scheduled" | "completed";

export interface InspectionReport {
  id: number;
  request: number;
  findings: string;
  certificate_file: string | null;
  gps_lat: string | null;
  gps_lng: string | null;
  submitted_at: string;
  photos: { id: number; image: string; caption: string }[];
}

export interface InspectionRequest {
  id: number;
  order: number;
  status: InspectionStatus;
  inspector: number | null;
  created_at: string;
  report: InspectionReport | null;
}

export interface AppNotification {
  id: number;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  owner: number;
  content_type: string;
  object_id: number;
  doc_type: "po" | "invoice" | "certificate" | "delivery_note" | "other";
  file: string;
  version: number;
  uploaded_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
