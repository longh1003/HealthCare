from datetime import datetime, time, timedelta

import pytz
from django.db.models import Max
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from healthcare import perms, paginators
from healthcare.models import User, MedicalRecord, MedicalRecordDetail, Medication, RealTimeChat, Status, Sickness, \
    DiagnosisPeriod, Role
from rest_framework import viewsets, generics, status, permissions, serializers

from healthcare.serializers import MedicalRecordDetailSerializer, UserSerializer, MedicalRecordSerializer, \
    ChatSerializer, ChatNoUsersSerializer, MedicationSerializer, DiagnosisPeriodSerializer


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False, url_path='current-user', permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        return Response(UserSerializer(request.user).data)


class MedicalRecordViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = MedicalRecord.objects.select_related('user').filter(active=True)
    serializer_class = MedicalRecordSerializer

    # permission_classes = [perms.MROwnerPerm]

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH']:
            return [perms.MROwnerPerm()]

        return [permissions.AllowAny()]

    def list(self, request):
        queryset = MedicalRecord.objects.filter(active=True)
        p = paginators.MedicalRecordPaginator()
        page = p.paginate_queryset(queryset.order_by('id'), self.request)
        if page is not None:
            serializer = MedicalRecordSerializer(page, many=True)
            return p.get_paginated_response(serializer.data)
        else:
            serializer = MedicalRecordSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


def create(self, request):
    record = MedicalRecord.objects.filter(user=request.user, active=True)
    if record.exists():
        return Response("Only 1 medical record per user!", status=status.HTTP_400_BAD_REQUEST)
    else:
        serializer = MedicalRecordSerializer(data={
            'user': request.user.pk,
            'treatment_history': request.data.get('treatment_history')
        })
        serializer.is_valid(raise_exception=True)
        c = serializer.save()
        return Response(MedicalRecordSerializer(c).data, status=status.HTTP_201_CREATED)


def partial_update(self, request, pk=None):
    record = get_object_or_404(self.queryset, id=self.kwargs["pk"])
    self.check_object_permissions(self.request, record)
    serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


@action(['get', 'patch'], detail=True, url_path='detail')
def get_detail_med_record(self, request, pk=None):
    if request.method.__eq__('GET'):
        med_record_detail = get_object_or_404(MedicalRecordDetail.objects.filter(active=True), id=pk)
        serializer = MedicalRecordDetailSerializer(med_record_detail)
        return Response(serializer.data)

# thieu post cho med record detail(cho nhung lan kham sau)

# @action(['get', 'post'], detail=True, url_path='medication')
# def get_medication(self, request, pk=None):
#     if request.method.__eq__('GET'):
#         medication = Medication.objects.filter(active=True, med_record=pk)
#         if medication is None:
#             return Response("Medication can't be found")
#
#         else:
#             self.check_object_permissions(self.request, medication)
#             p = paginators.MedicationPaginator()
#             page = p.paginate_queryset(medication.order_by('id'), self.request)
#             if page is not None:
#                 serializer = MedicationSerializer(page, many=True)
#                 return p.get_paginated_response(serializer.data)
#             else:
#                 serializer = MedicationSerializer(medication, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method.__eq__('POST'):
#         name = request.data.get('name')
#         instruction = request.data.get('instruction')
#         attention = request.data.get('attention')
#         serializer = MedicationSerializer(data={
#             "med_record": pk,
#             "name": name,
#             "instruction": instruction,
#             "attention": attention
#         })
#
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
# # @action(['get', 'post'], detail=True, url_path='medication')
# # def get_sickness(self, request, pk=None):
# #     if request.method.__eq__('GET'):
# #         sickness = Sickness.objects.filter(active=True, med_record=pk)
# #         if sickness is None:
# #             return Response("Medication can't be found")
# #
# #         else:
# #             self.check_object_permissions(self.request, medication)
# #             p = paginators.MedicationPaginator()
# #             page = p.paginate_queryset(medication.order_by('id'), self.request)
# #             if page is not None:
# #                 serializer = MedicationSerializer(page, many=True)
# #                 return p.get_paginated_response(serializer.data)
# #             else:
# #                 serializer = MedicationSerializer(medication, many=True)
# #                 return Response(serializer.data, status=status.HTTP_200_OK)
# #
# #     elif request.method.__eq__('POST'):
# #         name = request.data.get('name')
# #         instruction = request.data.get('instruction')
# #         attention = request.data.get('attention')
# #         serializer = MedicationSerializer(data={
# #             "med_record": pk,
# #             "name": name,
# #             "instruction": instruction,
# #             "attention": attention
# #         })
# #
# #         serializer.is_valid(raise_exception=True)
# #         serializer.save()
# #
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicalRecordDetailViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action.__eq__('choose_diagnosis_period'):
            return [perms.OwnerDetailPerm()]
        if self.action.__eq__('post_auto_schedule'):
            return [perms.AdminPerm()]
        if self.request.method in ['PATCH']:
            return [perms.DoctorRecordPerm()]

        return [permissions.AllowAny()]

    def list(self, request):
        queryset = MedicalRecordDetail.objects.filter(active=True)
        p = paginators.MedicalRecordDetailPaginator()
        page = p.paginate_queryset(queryset.order_by('id'), self.request)
        if page is not None:
            serializer = MedicalRecordDetailSerializer(page, many=True)
            return p.get_paginated_response(serializer.data)
        else:
            serializer = MedicalRecordDetailSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        # chi cho doctor
        med_record_detail = get_object_or_404(MedicalRecordDetail.objects.filter(active=True), id=pk)
        symptoms = request.data.get('symptoms')
        diagnosis = request.data.get('diagnosis')

        if med_record_detail.diagnosis_period_id is None:
            return Response('Register for diagnose first!', status=status.HTTP_400_BAD_REQUEST)

        period = DiagnosisPeriod.objects.filter(active=True, id=med_record_detail.diagnosis_period_id)
        self.check_object_permissions(self.request, period)
        if period.exists() is None:
            return Response('Not such period available!', status=status.HTTP_400_BAD_REQUEST)
        elif datetime.now(tz=pytz.UTC) < period[0].fromDateTime:
            return Response('Cannot make change before the period')

        if symptoms is None and diagnosis is None:
            return Response('Missing symptoms, diagnosis', status=status.HTTP_400_BAD_REQUEST)

        if symptoms is not None or diagnosis is not None:
            serializer = MedicalRecordDetailSerializer(med_record_detail, data={
                "symptoms": symptoms,
                "diagnosis": diagnosis
            }, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=False, url_path='schedule')
    def get_diagnosis_period(self, request):
            period = DiagnosisPeriod.objects.filter(active=True)
            p = paginators.DiagnosisPeriodPaginator()
            page = p.paginate_queryset(period.order_by('id'), self.request)
            if page is not None:
                serializer = DiagnosisPeriodSerializer(page, many=True)
                return p.get_paginated_response(serializer.data)
            else:
                serializer = DiagnosisPeriodSerializer(period, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post', 'delete'], detail=True, url_path='schedule')
    def choose_diagnosis_period(self, request, pk=None):
        if request.method.__eq__('POST'):
            data = request.data.get('diagnosis_period')
            if data is None:
                return Response("id is missing", status=status.HTTP_400_BAD_REQUEST)

            record_detail = MedicalRecordDetail.objects.filter(active=True, med_record=pk, diagnosis_period=data)
            med_record = get_object_or_404(MedicalRecord.objects.filter(id=record_detail[0].med_record_id))
            self.check_object_permissions(self.request, med_record)

            if record_detail.exists():
                return Response("Choose already!", status=status.HTTP_400_BAD_REQUEST)

            else:
                period = DiagnosisPeriod.objects.get(active=True, id=data)
                if datetime.now(tz=pytz.UTC) >= period.fromDateTime:
                    return Response('You can not do this right now.', status=status.HTTP_400_BAD_REQUEST)
                if period.current_requests < period.max_requests:
                    serializer = MedicalRecordDetailSerializer(data={
                        "med_record": pk,
                        "diagnosis_period": data
                    })
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    period.current_requests += 1
                    period.save()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response("Max request reached!!!")

        else:
            record_detail = get_object_or_404(MedicalRecordDetail.objects.filter(active=True), id=pk)
            med_record = get_object_or_404(MedicalRecord.objects.filter(id=record_detail[0].med_record_id))
            self.check_object_permissions(self.request, med_record)
            created_date = record_detail.created_date
            today = datetime.today().replace(tzinfo=pytz.UTC)
            limit = timedelta(days=1, hours=0, minutes=0, seconds=0) + created_date
            limit_dt = created_date.replace(year=limit.year, month=limit.month, day=limit.day)
            if today > limit_dt:
                return Response("24 hours has passed!", status=status.HTTP_400_BAD_REQUEST)
            else:
                record_detail.diagnosis_period_id = None
                record_detail.save()
                serializer = MedicalRecordDetailSerializer(record_detail)

                return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False, url_path='schedule-auto')
    def post_auto_schedule(self, request):
        admin = get_object_or_404(Role.objects.filter(active=True, name='ADMIN'))
        self.check_object_permissions(self.request, admin)
        period = DiagnosisPeriod.objects.aggregate(max=Max('fromDateTime'))
        d = period['max']
        t = datetime.today().date()
        d = d.date() if period['max'] is not None else t

        if d > t:
            return Response("Clock error", status=status.HTTP_400_BAD_REQUEST)
        elif d == t:
            t += timedelta(days=1, hours=0, minutes=0, seconds=0)
            day = t.day
            month = t.month
            year = t.year
        else:
            day = t.day
            month = t.month
            year = t.year

        f_day = f'{day}' if day > 9 else f'0{day}'
        f_month = f'{month}' if month > 9 else f'0{month}'
        str_date = f'{year}{f_month}{f_day}'
        created_date = datetime.fromisoformat(str_date)
        time_list = [{"fromTime": "00:00:00+00:00", "toTime": "08:59:00+00:00"},
                     {"fromTime": "09:00:00+00:00", "toTime": "14:59:00+00:00"},
                     {"fromTime": "15:00:00+00:00", "toTime": "23:59:00+00:00"}]

        for time1 in time_list:
            from_date = time.fromisoformat(time1['fromTime'])
            from_date = datetime.combine(created_date, from_date, tzinfo=pytz.UTC)
            to_date = time.fromisoformat(time1['toTime'])
            to_date = datetime.combine(created_date, to_date, tzinfo=pytz.UTC)
            doctors = User.objects.filter(is_active=True, role=3)

            for doctor in doctors:
                serializer = DiagnosisPeriodSerializer(data={
                    "fromDateTime": from_date,
                    "toDateTime": to_date,
                    "max_requests": 5,
                    "current_requests": 0,
                    "user": doctor.id
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return Response('Success', status=status.HTTP_201_CREATED)


class MedicationViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Medication.objects.select_related('med_record').filter(active=True)
    serializer_class = MedicationSerializer


class ChatViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = RealTimeChat.objects.prefetch_related('users').filter(active=True)
    serializer_class = ChatSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH']:
            return [perms.ChatOwnerPerm()]

        return [permissions.AllowAny()]

    def create(self, request):
        chat_box = request.data.get('chat_box')
        if chat_box is None:
            return Response("chat_box is required", status=status.HTTP_400_BAD_REQUEST)
        serializer = ChatNoUsersSerializer(data={
            "chat_box": f'{request.user.username}:{chat_box}',
            "status": 3
        })

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.users.add(request.user)

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        chat = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(self.request, chat)
        status_request = request.data.get('status')

        if status_request in ['OPEN', 'CLOSE'] and request.data.get('chat_box') is not None:
            status = Status.objects.get(name__exact=status_request)
            chat_box = f'{chat.chat_box} # {request.user.username}:{request.data["chat_box"]} # '
            chat.status = status.id

            serializer = ChatSerializer(chat, partial=True, data={
                "chat_box": chat_box,
                "status": chat.status
            })
        elif status_request in ['OPEN', 'CLOSE']:
            status = Status.objects.get(name__exact=status_request)
            chat.status = status

            serializer = ChatSerializer(chat, partial=True, data={
                "status": chat.status
            })
        else:
            chat_box = f'{chat.chat_box} # {request.user.username}:{request.data["chat_box"]} # '

            serializer = ChatSerializer(chat, partial=True, data={
                "chat_box": chat_box
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        chat.users.add(request.user)

        return Response(serializer.data)
