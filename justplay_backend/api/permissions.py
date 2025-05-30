from rest_framework.permissions import BasePermission, SAFE_METHODS


# 🔒 ADMIN UNIQUEMENT
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# 🧩 ADMIN ou LECTURE SEULE
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


# 🔐 SEULEMENT EXPLOITANT
class IsExploitantUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'exploitant'


# 🔐 ADMIN ou EXPLOITANT
class IsAdminOrExploitant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'exploitant']


# 🔒 CLIENT UNIQUEMENT
class IsClientUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


# ✅ PROPRIÉTAIRE UNIQUEMENT
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
 