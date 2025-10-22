from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from main.models import Post


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission, allowing only the author to edit the object"""

    def has_object_permission(self, request: Request, view: APIView, obj: Post) -> bool:
        # All can read object
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only author can edit
        return obj.author == request.user
