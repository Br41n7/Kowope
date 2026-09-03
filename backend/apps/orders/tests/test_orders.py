import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.marketplace.models import RFQ, Offer
from apps.orders.models import PurchaseOrder

User = get_user_model()


@pytest.mark.django_db
def test_terms_snapshot_is_immutable_after_creation():
    buyer = User.objects.create_user(username="b1", password="pass12345", role="buyer", is_kyc_verified=True)
    seller = User.objects.create_user(username="s1", password="pass12345", role="seller", is_kyc_verified=True)
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Rice", quantity=100, delivery_location="Kebbi",
        delivery_date="2026-12-01", target_price=400,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=420, delivery_period="10 days")

    from core.services.offer_service import accept_offer
    order = accept_offer(offer, buyer)

    original_price = order.terms_snapshot["price"]
    rfq.target_price = 999
    rfq.save()

    order.refresh_from_db()
    assert order.terms_snapshot["price"] == original_price


@pytest.mark.django_db
def test_only_buyer_or_seller_can_view_their_order():
    buyer = User.objects.create_user(username="b2", password="pass12345", role="buyer", is_kyc_verified=True)
    seller = User.objects.create_user(username="s2", password="pass12345", role="seller", is_kyc_verified=True)
    outsider = User.objects.create_user(username="x2", password="pass12345", role="buyer")

    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Yam", quantity=30, delivery_location="Enugu",
        delivery_date="2026-12-01", target_price=100,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=110, delivery_period="5 days")
    from core.services.offer_service import accept_offer
    order = accept_offer(offer, buyer)

    client = APIClient()
    client.force_authenticate(user=outsider)
    resp = client.get(f"/api/v1/orders/{order.id}/")
    assert resp.status_code == 404  # filtered out of queryset, not just permission-denied


@pytest.mark.django_db
def test_cannot_set_arbitrary_status_via_api():
    buyer = User.objects.create_user(username="b3", password="pass12345", role="buyer", is_kyc_verified=True)
    seller = User.objects.create_user(username="s3", password="pass12345", role="seller", is_kyc_verified=True)
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Millet", quantity=15, delivery_location="Sokoto",
        delivery_date="2026-12-01", target_price=90,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=95, delivery_period="3 days")
    from core.services.offer_service import accept_offer
    order = accept_offer(offer, buyer)

    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.patch(f"/api/v1/orders/{order.id}/", {"status": "issued"}, format="json")
    # 'issued' is the initial status, not in ALLOWED_SELF_SERVICE_STATUSES -> rejected
    assert resp.status_code == 400
