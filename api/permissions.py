from rest_framework import permissions


class IsPartner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'shop':
            return True
