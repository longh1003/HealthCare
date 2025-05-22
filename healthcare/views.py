

from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from healthcare import perms, paginators
from healthcare.models import User, MedicalRecord, MedicalRecordDetail, Medication, RealTimeChat, Status, Sickness, \
    DiagnosisPeriod
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
        if self.action.__eq__('get_medication'):
            return [perms.MedicationPerm()]
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH']:
            return [perms.MROwnerPerm()]

        return [permissions.AllowAny()]

    def list(self, request):
        queryset = MedicalRecord.objects.filter(active=True)
        serializer = MedicalRecordSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        record = MedicalRecord.objects.filter(user=request.user).first()
        if record is not None:
            print(record)
            return Response("Only 1 medical record per user!", status=status.HTTP_400_BAD_REQUEST)
        serializer = MedicalRecordSerializer(data={
            'user': request.user.pk,
            'treatment_history': request.data.get('treatment_history')
        })
        serializer.is_valid(raise_exception=True)
        c = serializer.save()
        return Response(MedicalRecordSerializer(c).data, status=status.HTTP_201_CREATED)

    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj

    def partial_update(self, request, pk=None):
        record = self.get_object()
        serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=True, url_path='detail')
    def get_detail_med_record(self, pk=None):
            med_record_detail = get_object_or_404(MedicalRecordDetail.objects.filter(active=True), id=pk)
            serializer = MedicalRecordDetailSerializer(med_record_detail)
            return Response(serializer.data)
    # thieu post cho med record detail(cho nhung lan kham sau)

    @action(['get', 'post'], detail=True, url_path='schedule')
    def get_diagnosis_period(self, request, pk=None):
        if request.method.__eq__('GET'):
            period = DiagnosisPeriod.objects.filter(active=True)
            serializer = DiagnosisPeriodSerializer(period, many=True)
            return Response(serializer.data)

        if request.method.__eq__('POST'):
            data = request.data.get('diagnosis_period')
            if data is None:
                return Response("id is missing", status=status.HTTP_400_BAD_REQUEST)

            period = DiagnosisPeriod.objects.get(active=True, id=data)
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


    @action(['get', 'post'], detail=True, url_path='medication')
    def get_medication(self, request, pk=None):
        if request.method.__eq__('GET'):
            medication = Medication.objects.filter(active=True, med_record=pk)
            if medication is None:
                return Response("Medication can't be found")

            else:
                self.check_object_permissions(self.request, medication)
                p = paginators.MedicationPaginator()
                page = p.paginate_queryset(medication.order_by('id'), self.request)
                if page is not None:
                    serializer = MedicationSerializer(page, many=True)
                    return p.get_paginated_response(serializer.data)
                else:
                    serializer = MedicationSerializer(medication, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method.__eq__('POST'):
            name = request.data.get('name')
            instruction = request.data.get('instruction')
            attention = request.data.get('attention')
            serializer = MedicationSerializer(data={
                "med_record": pk,
                "name": name,
                "instruction": instruction,
                "attention": attention
            })

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(['get', 'post'], detail=True, url_path='medication')
    # def get_sickness(self, request, pk=None):
    #     if request.method.__eq__('GET'):
    #         sickness = Sickness.objects.filter(active=True, med_record=pk)
    #         if sickness is None:
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

