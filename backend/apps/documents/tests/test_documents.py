import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.marketplace.models import RFQ, Offer
from apps.orders.models import PurchaseOrder
from core.services.offer_service import accept_offer

User = get_user_model()


def make_user(username, role):
    u = User.objects.create_user(username=username, password="pass12345", role=role)
    u.is_kyc_verified = True
    u.save()
    return u


@pytest.fixture
def order():
    buyer = make_user("doc_buyer", "buyer")
    seller = make_user("doc_seller", "seller")
    rfq = RFQ.objects.create(
        buyer=buyer, commodity="Shea Butter", quantity=8, delivery_location="Kaduna",
        delivery_date="2026-12-01", target_price=200,
        quality_verification_pref="sample", payment_pref="escrow",
    )
    offer = Offer.objects.create(rfq=rfq, seller=seller, price=210, delivery_period="5 days")
    return accept_offer(offer, buyer)


def _upload(client, order_id, filename="invoice.pdf"):
    ct = ContentType.objects.get_for_model(PurchaseOrder)
    f = SimpleUploadedFile(filename, b"%PDF fake bytes", content_type="application/pdf")
    return client.post("/api/v1/documents", {
        "content_type": ct.model, "object_id": order_id, "doc_type": "invoice", "file": f,
    }, format="multipart")


@pytest.mark.django_db
def test_order_participant_can_upload_document(order):
    client = APIClient()
    client.force_authenticate(user=order.seller)
    resp = _upload(client, order.id)
    assert resp.status_code == 201
    assert resp.data["file"].startswith("/media/")  # relative, not an absolute internal-host URL


@pytest.mark.django_db
def test_non_participant_cannot_upload_document(order):
    outsider = make_user("doc_outsider", "buyer")
    client = APIClient()
    client.force_authenticate(user=outsider)
    resp = _upload(client, order.id)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_non_participant_cannot_see_document_in_list(order):
    client = APIClient()
    client.force_authenticate(user=order.buyer)
    _upload(client, order.id)

    outsider = make_user("doc_outsider2", "seller")
    outsider_client = APIClient()
    outsider_client.force_authenticate(user=outsider)
    ct = ContentType.objects.get_for_model(PurchaseOrder)
    resp = outsider_client.get(f"/api/v1/documents?content_type={ct.model}&object_id={order.id}")
    assert resp.status_code == 200
    assert resp.data["results"] == []


@pytest.mark.django_db
def test_document_version_increments_per_doc_type(order):
    client = APIClient()
    client.force_authenticate(user=order.buyer)
    r1 = _upload(client, order.id, "invoice_v1.pdf")
    r2 = _upload(client, order.id, "invoice_v2.pdf")
    assert r1.data["version"] == 1
    assert r2.data["version"] == 2


@pytest.mark.django_db
def test_admin_can_see_any_order_documents(order):
    client = APIClient()
    client.force_authenticate(user=order.seller)
    _upload(client, order.id)

    admin = make_user("doc_admin", "admin")
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    ct = ContentType.objects.get_for_model(PurchaseOrder)
    resp = admin_client.get(f"/api/v1/documents?content_type={ct.model}&object_id={order.id}")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
