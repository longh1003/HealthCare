from django.contrib.auth.models import AbstractUser
from django.db import models


class OnlyActive(models.Model):
    active = models.BooleanField(default=True)
    class Meta:
        abstract = True

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(BaseModel):
    name = models.CharField(max_length=20, default="USER")

    def __str__(self):
        return self.name


class User1(AbstractUser):
    date_of_birth = models.DateField(auto_now_add=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField(default="Not specify")

    class Meta:
        abstract = True


class User(User1):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=1)



class MedicalRecord(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="md_user", default=3)
    treatment_history = models.TextField(null=True)

    def __str__(self):
        return f"{self.user} {self.treatment_history}"


class MedicalRecordDetail(BaseModel):
    med_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name="med_record")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mrd_doctor", default=3)
    symptoms = models.TextField(null=True) #nullable
    diagnosis = models.TextField(null=True) #nullable
    treatment_date = models.DateTimeField() #dang ki lich kham

    #if user.role != 'Doctor' error
    def __str__(self):
        return str(self.med_record)


class Status(BaseModel):
    name = models.CharField(max_length=20)
    for_doctor = models.BooleanField(default=False)
    for_payment = models.BooleanField(default=False)
    for_chat = models.BooleanField(default=False)
    for_sickness = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DiagnosisPeriod(OnlyActive):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dp_doctor", default=3)
    fromDateTime = models.DateTimeField()
    toDateTime = models.DateTimeField()
    max_requests = models.IntegerField(default=5)
    current_requests = models.IntegerField(default=0)
    status = models.ForeignKey(Status, default=1, on_delete=models.CASCADE, limit_choices_to={'for_doctor': 1})

    def __str__(self):
        # id = DiagnosisPeriod.doctor
        # user = User.objects.get(id=id)
        return self.user.username


class Sickness(BaseModel):
    med_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE) #foreign key to medicalrecord_id
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, limit_choices_to={'for_sickness': 1}) #foreign key to status.id

    def __str__(self):
        return self.name


class Medication(BaseModel):
    med_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE) #foreign key to medicalrecord.id
    name = models.CharField(max_length=255)
    instruction = models.TextField(null=True)
    attention = models.TextField(null=True)

    def __str__(self):
        return self.name

class RealTimeChat(BaseModel):
    users = models.ManyToManyField('User')
    chat_box = models.TextField(null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, limit_choices_to={'for_chat': 1}) #foreign key


class Payment(BaseModel):
    med_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE) #foreign key to MedicalRecord.id
    method = models.TextField(null=True)
    hospital_fee = models.FloatField(default=0)
    status = models.ForeignKey(Status, default=None, on_delete=models.CASCADE, limit_choices_to={'for_payment': 1}) #foreign key

    def __str__(self):
        return str(self.med_record)

class Evaluation(BaseModel):
    med_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)  #foreign key to MedicalRecord.id
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    feedback = models.TextField(null=True)

    def __str__(self):
        return str(self.med_record)
