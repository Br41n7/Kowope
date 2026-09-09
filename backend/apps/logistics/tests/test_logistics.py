import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.logistics.models import LogisticsRequest
from apps.marketplace.models import RFQ, Offer
from core.services.offer_service import accept_offer

User = get_user_model()


def make_user(username, role):
    u = User.objects.create_user(username=username, password="pass12345", role=role)
    u.is_kyc_verified = True
    u.save()
    return u


@pytest.fixture
def order():
    buyer = make_user("log_buyer", "buyer")
    seller = make_user("log_seller", "seller")
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Timber", quantity=10, delivery_location="Calabar",
        delivery_date="2026-12-01", target_price=500,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=520, delivery_period="7 days")
    return accept_offer(offer, buyer)


@pytest.mark.django_db
def test_unrelated_buyer_cannot_create_logistics_request(order):
    outsider = make_user("log_outsider", "buyer")
    client = APIClient()
    client.force_authenticate(user=outsider)
    resp = client.post("/api/v1/logistics-requests", {
        "order": order.id, "pickup_location": "A", "delivery_location": "B",
    }, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_seller_can_create_logistics_request(order):
    client = APIClient()
    client.force_authenticate(user=order.seller)
    resp = client.post("/api/v1/logistics-requests", {
        "order": order.id, "pickup_location": "Warehouse", "delivery_location": "Port",
    }, format="json")
    assert resp.status_code == 201


@pytest.mark.django_db
def test_only_logistics_role_can_assign(order):
    lr = LogisticsRequest.objects.create(order=order, pickup_location="A", delivery_location="B")
    buyer_client = APIClient()
    buyer_client.force_authenticate(user=order.buyer)
    resp = buyer_client.post(f"/api/v1/logistics-requests/{lr.id}/assign", format="json")
    assert resp.status_code == 403

    partner = make_user("log_partner", "logistics")
    partner_client = APIClient()
    partner_client.force_authenticate(user=partner)
    resp = partner_client.post(f"/api/v1/logistics-requests/{lr.id}/assign", format="json")
    assert resp.status_code == 200
    lr.refresh_from_db()
    assert lr.assigned_partner == partner
    assert lr.status == LogisticsRequest.Status.ASSIGNED


@pytest.mark.django_db
def test_cannot_double_assign(order):
    partner1 = make_user("log_p1", "logistics")
    partner2 = make_user("log_p2", "logistics")
    lr = LogisticsRequest.objects.create(order=order, pickup_location="A", delivery_location="B")

    c1 = APIClient(); c1.force_authenticate(user=partner1)
    c1.post(f"/api/v1/logistics-requests/{lr.id}/assign", format="json")

    # A different, uninvolved partner can no longer even see the job once it's claimed —
    # 404, not 400: the queryset itself hides jobs assigned to someone else.
    c2 = APIClient(); c2.force_authenticate(user=partner2)
    resp = c2.post(f"/api/v1/logistics-requests/{lr.id}/assign", format="json")
    assert resp.status_code == 404

    # The assigned partner re-attempting hits the explicit guard clause instead.
    resp = c1.post(f"/api/v1/logistics-requests/{lr.id}/assign", format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_only_assigned_partner_can_add_update(order):
    partner = make_user("log_p3", "logistics")
    other_partner = make_user("log_p4", "logistics")
    lr = LogisticsRequest.objects.create(
        order=order, pickup_location="A", delivery_location="B",
        assigned_partner=partner, status=LogisticsRequest.Status.ASSIGNED,
    )

    # An uninvolved partner can't even see a job assigned to someone else (404, not 403) —
    # the queryset itself is the access boundary here.
    other_client = APIClient(); other_client.force_authenticate(user=other_partner)
    resp = other_client.post(f"/api/v1/logistics-requests/{lr.id}/updates", {"status": "in_transit"}, format="json")
    assert resp.status_code == 404

    partner_client = APIClient(); partner_client.force_authenticate(user=partner)
    resp = partner_client.post(f"/api/v1/logistics-requests/{lr.id}/updates", {"status": "in_transit"}, format="json")
    assert resp.status_code == 201


@pytest.mark.django_db
def test_logistics_partner_sees_open_pool_and_own_jobs(order):
    partner = make_user("log_p5", "logistics")
    open_job = LogisticsRequest.objects.create(order=order, pickup_location="A", delivery_location="B")
    other_partner = make_user("log_p6", "logistics")
    someone_elses_job = LogisticsRequest.objects.create(
        order=order, pickup_location="C", delivery_location="D",
        assigned_partner=other_partner, status=LogisticsRequest.Status.ASSIGNED,
    )
    client = APIClient(); client.force_authenticate(user=partner)
    resp = client.get("/api/v1/logistics-requests")
    ids = [r["id"] for r in resp.data["results"]]
    assert open_job.id in ids
    assert someone_elses_job.id not in ids
