import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.marketplace.models import RFQ, Offer
from apps.orders.models import PurchaseOrder

User = get_user_model()


def make_user(username, role):
    u = User.objects.create_user(username=username, password="pass12345", role=role)
    u.is_kyc_verified = True
    u.save()
    return u


@pytest.fixture
def buyer():
    return make_user("buyer_a", "buyer")


@pytest.fixture
def seller():
    return make_user("seller_a", "seller")


@pytest.mark.django_db
def test_buyer_can_create_rfq(buyer):
    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.post("/api/v1/rfqs", {
        "commodity": "Cocoa", "quantity": "100", "unit": "MT",
        "delivery_location": "Apapa", "delivery_date": "2026-12-31",
        "target_price": "300", "quality_verification_pref": "sample", "payment_pref": "escrow",
    }, format="json")
    assert resp.status_code == 201
    assert resp.data["status"] == "open"


@pytest.mark.django_db
def test_cannot_offer_on_closed_rfq(buyer, seller):
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Maize", quantity=50, delivery_location="Kano",
        delivery_date="2026-12-01", target_price=200,
        quality_verification_pref="sample", payment_pref="escrow", status=RFQ.Status.CLOSED,
    )
    client = APIClient()
    client.force_authenticate(user=seller)
    resp = client.post("/api/v1/offers", {"rfq": rfq.id, "price": "210", "delivery_period": "10 days"}, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_accept_offer_creates_purchase_order_and_closes_rfq(buyer, seller):
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Sesame", quantity=20, delivery_location="Kaduna",
        delivery_date="2026-12-01", target_price=500,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=520, delivery_period="7 days")

    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.post(f"/api/v1/offers/{offer.id}/accept", format="json")

    assert resp.status_code == 201
    assert PurchaseOrder.objects.filter(offer=offer).exists()
    rfq.refresh_from_db()
    offer.refresh_from_db()
    assert rfq.status == RFQ.Status.CLOSED
    assert offer.status == Offer.Status.ACCEPTED


@pytest.mark.django_db
def test_only_rfq_buyer_can_accept_offer(buyer, seller):
    other_buyer = make_user("buyer_b", "buyer")
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Ginger", quantity=10, delivery_location="Jos",
        delivery_date="2026-12-01", target_price=800,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=850, delivery_period="5 days")

    client = APIClient()
    client.force_authenticate(user=other_buyer)
    resp = client.post(f"/api/v1/offers/{offer.id}/accept", format="json")
    assert resp.status_code == 403
