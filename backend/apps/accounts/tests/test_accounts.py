import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import KYCProfile

User = get_user_model()


@pytest.mark.django_db
def test_register_creates_user_and_sets_auth_cookies():
    client = APIClient()
    resp = client.post("/api/v1/auth/register", {
        "username": "buyer1", "email": "b@example.com", "password": "StrongPass123!", "role": "buyer",
    }, format="json")
    assert resp.status_code == 201
    assert "ta_access" in resp.cookies
    assert resp.cookies["ta_access"]["httponly"]
    assert "ta_refresh" in resp.cookies
    assert User.objects.filter(username="buyer1").exists()


@pytest.mark.django_db
def test_login_sets_cookies_and_me_endpoint_works_via_cookie():
    User.objects.create_user(username="buyer_login", password="StrongPass123!", role="buyer")
    client = APIClient()
    resp = client.post("/api/v1/auth/login", {"username": "buyer_login", "password": "StrongPass123!"}, format="json")
    assert resp.status_code == 200
    assert "ta_access" in resp.cookies

    # The test client persists cookies across requests automatically, mirroring a browser.
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.data["username"] == "buyer_login"


@pytest.mark.django_db
def test_logout_clears_cookies():
    User.objects.create_user(username="buyer_logout", password="StrongPass123!", role="buyer")
    client = APIClient()
    client.post("/api/v1/auth/login", {"username": "buyer_logout", "password": "StrongPass123!"}, format="json")
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401


@pytest.mark.django_db
def test_kyc_submit_sets_pending_status():
    user = User.objects.create_user(username="seller1", password="pass12345", role="seller")
    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.post("/api/v1/kyc/submit", {"business_name": "Seller Co"}, format="json")
    assert resp.status_code == 201
    assert resp.data["status"] == "pending"


@pytest.mark.django_db
def test_only_admin_can_review_kyc():
    seller = User.objects.create_user(username="seller2", password="pass12345", role="seller")
    KYCProfile.objects.create(user=seller, business_name="Seller Co")
    client = APIClient()
    client.force_authenticate(user=seller)
    profile = KYCProfile.objects.get(user=seller)
    resp = client.patch(f"/api/v1/kyc-review/{profile.id}", {"status": "approved"}, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_admin_approving_kyc_marks_user_verified():
    admin = User.objects.create_user(username="admin1", password="pass12345", role="admin")
    seller = User.objects.create_user(username="seller3", password="pass12345", role="seller")
    profile = KYCProfile.objects.create(user=seller, business_name="Seller Co")
    client = APIClient()
    client.force_authenticate(user=admin)
    resp = client.patch(f"/api/v1/kyc-review/{profile.id}", {"status": "approved"}, format="json")
    assert resp.status_code == 200
    seller.refresh_from_db()
    assert seller.is_kyc_verified is True
