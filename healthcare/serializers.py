from rest_framework import serializers

from healthcare.models import User, MedicalRecord, MedicalRecordDetail, RealTimeChat, Status


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

    def get_fullname(self, obj):
        return f'{obj.last_name} {obj.first_name}'

    def get_role(self, obj):
        return obj.role.name


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'contact_number', 'is_active', 'password']

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
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = MedicalRecord
        fields = '__all__'


class MedicalRecordDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalRecordDetail
        fields = ['id', 'active']


class ChatSerializer(serializers.ModelSerializer):
    users = MinimalUserSerializer(many=True)
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.status.name

    class Meta:
        model = RealTimeChat
        fields = '__all__'

# class DoctorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Doctor
#         fields = '__all__'
