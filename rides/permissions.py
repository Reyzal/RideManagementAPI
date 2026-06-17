from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Only users with the admin role can access this endpoint."

    def has_permission(self, request, view):
        return bool(
            request.user
            and getattr(request.user, "role", None) == "admin"
        )