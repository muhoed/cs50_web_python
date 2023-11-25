from rest_framework import permissions

from .models import WiseGroceryUser


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # All permissions are only allowed to the owner of the snippet.
        sysuser = WiseGroceryUser.objects.get(username='sysuser')
        return obj.created_by == request.user or obj.created_by == sysuser
        