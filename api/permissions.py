from rest_framework import permissions


class IsPartner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.type == 'shop'


class IsShopOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_superuser)
