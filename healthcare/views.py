

from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


from healthcare import perms
from healthcare.models import User, MedicalRecord, MedicalRecordDetail, Medication, RealTimeChat
from rest_framework import viewsets, generics, status, permissions, serializers

from healthcare.serializers import MedicalRecordDetailSerializer, UserSerializer, MedicalRecordSerializer, ChatSerializer


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False, url_path='current-user', permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        return Response(UserSerializer(request.user).data)


class MedicalRecordViewSet(viewsets.ViewSet):
    queryset = MedicalRecord.objects.select_related('user').filter(active=True)
    # permission_classes = [perms.MROwnerPerm]

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH']:
            return [perms.MROwnerPerm()]

        return [permissions.AllowAny()]

    def list(self, request):
        queryset = MedicalRecord.objects.filter(active=True)
        serializer = MedicalRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, pk=None):
        queryset = MedicalRecord.objects.filter(active=True)
        medical_record = get_object_or_404(queryset, pk=pk)
        serializer = MedicalRecordSerializer(medical_record)
        return Response(serializer.data)

    def create(self, request):
        serializer = MedicalRecordSerializer(data={
            'user': request.user.pk,
            'treatment_history': request.data.get('treatment_history')
        })
        serializer.is_valid(raise_exception=True)
        c = serializer.save()
        return Response(MedicalRecordSerializer(c).data, status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    #     treatment_history = request.data.get('treatment_history')
    #     if treatment_history is None:
    #         raise serializers.ValidationError("treatment_history is required")
    #
    #     q, created = MedicalRecord.objects.update_or_create(
    #         id=pk,
    #         user=request.user.pk,
    #         treatment_history=treatment_history
    #     )
    #     return Response(MedicalRecordSerializer(q).data, status=status.HTTP_200_OK)

    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        print(f'{self.request}, {obj}')

        return obj

    def partial_update(self, request, pk=None):
        record = self.get_object()
        serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=True, url_path='detail')
    def get_detail_med_record(self, request, pk=None):
        med_record_detail = get_object_or_404(MedicalRecordDetail.objects.filter(active=True), pk=pk)
        serializer = MedicalRecordDetailSerializer(med_record_detail)
        return Response(serializer.data)


class ChatViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = RealTimeChat.objects.prefetch_related('users').filter(active=True)
    serializer_class = ChatSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH']:
            return [perms.ChatOwnerPerm()]

        return [permissions.AllowAny()]

    def partial_update(self, request, pk=None):
        chat = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(self.request, chat)
        chat_box = f'{chat.chat_box} # {request.user.username}:{request.data["chat_box"]} # '
        serializer = ChatSerializer(chat, partial=True, data={
            "chat_box": chat_box
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        chat.users.add(request.user)

        return Response(serializer.data)
# class MedicalRecordDetailViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
#     queryset = MedicalRecordDetail.objects.filter(active=True)
#     serializer_class = serializers.MedicalRecordDetailSerializer
