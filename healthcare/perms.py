from rest_framework import permissions

from healthcare import models


class OwnerPerm(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user == obj


class MROwnerPerm(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        # print("check perm")
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class ChatOwnerPerm(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        doctor = False
        doctor_user = models.User.objects.filter(id__in=obj.users.all())
        if len(doctor_user) < 2:
            doctor = True
        return request.user.is_authenticated and doctor