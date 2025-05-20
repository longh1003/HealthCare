from rest_framework import permissions

from healthcare import models


class OwnerPerm(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user == obj


class MROwnerPerm(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        print(obj)
        return request.user.is_authenticated and obj.user == request.user


class ChatOwnerPerm(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        doctor = False
        doctor_user = models.User.objects.filter(id__in=obj.users.all())
        status_close = obj.status.name

        if status_close == 'CLOSE':
            status_close = False
        else:
            status_close = True

        if len(doctor_user) < 2:
            doctor = True

        return request.user.is_authenticated and doctor and status_close

class MedicationPerm(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        med_record = models.MedicalRecord.objects.get(id__exact=obj[0].med_record_id)
        return request.user.is_authenticated and request.user.id == med_record.user_id