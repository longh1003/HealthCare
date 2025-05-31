from rest_framework import serializers

from healthcare.models import User, MedicalRecord, MedicalRecordDetail, RealTimeChat, Status, Medication, Sickness, \
    DiagnosisPeriod


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['name']

class MinimalUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'role']
        # fields = ['id', 'fullname']

    def get_fullname(self, obj):
        return f'{obj.last_name} {obj.first_name}'

    def get_role(self, obj):
        return obj.role.name


class MedicationMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'first_name', 'last_name', 'email', 'contact_number', 'is_active']
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()

        return u

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()

        return instance


class MedicalRecordSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = MinimalUserSerializer(instance.user).data
        return data

    class Meta:
        model = MedicalRecord
        fields = '__all__'


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    # medication = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecordDetail
        fields = '__all__'

    # def get_medication(self, obj):
    #     return MedicationMinimalSerializer(obj.medication.all(), many=True).data


class ChatNoUsersSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.status.name

    class Meta:
        model = RealTimeChat
        fields = ['id', 'chat_box', 'status']

class ChatSerializer(ChatNoUsersSerializer):
    users = MinimalUserSerializer(many=True)

    class Meta:
        model = ChatNoUsersSerializer.Meta.model
        fields = ChatNoUsersSerializer.Meta.fields + ['users']


class MedicationSerializer(MedicationMinimalSerializer):
    class Meta:
        model = MedicationMinimalSerializer.Meta.model
        fields = MedicationMinimalSerializer.Meta.fields + ['record_detail', 'instruction', 'attention']


class SicknessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sickness
        fields = '__all__'


class DiagnosisPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisPeriod
        fields = '__all__'