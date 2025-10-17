from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission, allowing only the author to edit the object"""

    def has_object_permission(self, request, view, obj):
        # All can read object
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only author can edit
        return obj.author == request.user
