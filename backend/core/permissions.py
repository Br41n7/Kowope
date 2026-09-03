from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """Allows access only to users with role='admin' (or Django staff/superuser)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_staff or user.is_superuser or getattr(user, "role", None) == "admin")
        )


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "buyer")


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "seller")


class IsKYCVerified(BasePermission):
    message = "Your KYC must be approved before you can perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_kyc_verified)


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: only the object's `owner_field` attribute (set on the view) can edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner_field = getattr(view, "owner_field", "user")
        owner = getattr(obj, owner_field, None)
        return owner == request.user
