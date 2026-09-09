import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.marketplace.models import RFQ, Offer
from apps.quality.models import InspectionRequest
from core.services.offer_service import accept_offer

User = get_user_model()


def make_user(username, role):
    u = User.objects.create_user(username=username, password="pass12345", role=role)
    u.is_kyc_verified = True
    u.save()
    return u


@pytest.fixture
def order():
    buyer = make_user("q_buyer", "buyer")
    seller = make_user("q_seller", "seller")
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Sesame", quantity=10, delivery_location="Kano",
        delivery_date="2026-12-01", target_price=500,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=520, delivery_period="7 days")
    return accept_offer(offer, buyer)


@pytest.mark.django_db
def test_unrelated_user_cannot_create_inspection_request(order):
    outsider = make_user("q_outsider", "buyer")
    client = APIClient(); client.force_authenticate(user=outsider)
    resp = client.post("/api/v1/inspection-requests", {"order": order.id}, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_only_inspector_role_can_assign(order):
    ir = InspectionRequest.objects.create(order=order)
    buyer_client = APIClient(); buyer_client.force_authenticate(user=order.buyer)
    resp = buyer_client.post(f"/api/v1/inspection-requests/{ir.id}/assign", format="json")
    assert resp.status_code == 403

    inspector = make_user("q_inspector", "inspector")
    inspector_client = APIClient(); inspector_client.force_authenticate(user=inspector)
    resp = inspector_client.post(f"/api/v1/inspection-requests/{ir.id}/assign", format="json")
    assert resp.status_code == 200
    ir.refresh_from_db()
    assert ir.inspector == inspector
    assert ir.status == InspectionRequest.Status.SCHEDULED


@pytest.mark.django_db
def test_only_assigned_inspector_can_submit_report(order):
    inspector = make_user("q_i2", "inspector")
    other_inspector = make_user("q_i3", "inspector")
    ir = InspectionRequest.objects.create(order=order, inspector=inspector, status=InspectionRequest.Status.SCHEDULED)

    # An uninvolved inspector can't see a job scheduled to someone else — 404, not 403.
    other_client = APIClient(); other_client.force_authenticate(user=other_inspector)
    resp = other_client.post(f"/api/v1/inspection-requests/{ir.id}/report", {"findings": "x"}, format="json")
    assert resp.status_code == 404

    inspector_client = APIClient(); inspector_client.force_authenticate(user=inspector)
    resp = inspector_client.post(f"/api/v1/inspection-requests/{ir.id}/report", {"findings": "Grade A confirmed"}, format="json")
    assert resp.status_code == 201


@pytest.mark.django_db
def test_inspector_sees_open_pool_and_own_jobs(order):
    inspector = make_user("q_i4", "inspector")
    open_job = InspectionRequest.objects.create(order=order)
    other_inspector = make_user("q_i5", "inspector")
    someone_elses_job = InspectionRequest.objects.create(
        order=order, inspector=other_inspector, status=InspectionRequest.Status.SCHEDULED
    )
    client = APIClient(); client.force_authenticate(user=inspector)
    resp = client.get("/api/v1/inspection-requests")
    ids = [r["id"] for r in resp.data["results"]]
    assert open_job.id in ids
    assert someone_elses_job.id not in ids
