from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm

from healthcare.models import User, Status, Role, DiagnosisPeriod, MedicalRecord, MedicalRecordDetail, Medication, Evaluation, Payment, RealTimeChat, Sickness


class MyNewSite(admin.AdminSite):
    site_header = "Quản trị healthcare"
    site_title = "Healthcare"
    index_title = "Tùy chỉnh"


# /admin/course-stats
# def get_urls(self):
#     return [
#         path('course-stats/', self.stats_view)
#     ] + super().get_urls()

# def stats_view(self, request):
#     stats = Course.objects.annotate(lesson_count=Count('lesson__id')).values('id', 'subject', 'lesson_count')
#
#     return TemplateResponse(request, 'admin/stats_view.html', {
#         'stats': stats
#     })

new_site = MyNewSite(name='Quan tri Healthcare')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomUser(admin.ModelAdmin):
    model = User
    form = CustomUserChangeForm
    # list_display = ['username','first_name', 'last_name', 'date_of_birth', 'contact_number', 'role']
    list_display = ['username', 'first_name', 'last_name', 'date_of_birth', 'contact_number']


class CustomPeriod(admin.ModelAdmin):
    model = DiagnosisPeriod
    list_display = ['id', 'user', 'fromDateTime', 'toDateTime']


class CustomMedicalRecord(admin.ModelAdmin):
    model = MedicalRecord
    list_display = ['user', 'treatment_history']


class CustomMedicalRecordDetail(admin.ModelAdmin):
    model = MedicalRecordDetail
    list_display = ['med_record', 'symptoms', 'diagnosis', 'diagnosis_period']


class CustomMedication(admin.ModelAdmin):
    model = Medication
    list_display = ['record_detail', 'name', 'instruction', 'attention']


class CustomSickness(admin.ModelAdmin):
    model = Sickness
    list_display = ['record_detail', 'name', 'description', 'status']


class CustomRealTimeChat(admin.ModelAdmin):
    model = RealTimeChat
    list_display = ['display_users', 'chat_box', 'status']

    def display_users(self, obj):
        return ', '.join([user.username for user in obj.users.all()])

    display_users.short_description = 'Users'


class CustomPayment(admin.ModelAdmin):
    model = Payment
    list_display = ['record_detail', 'method', 'hospital_fee', 'status']


class CustomEvaluation(admin.ModelAdmin):
    model = Evaluation
    list_display = ['record_detail', 'rating', 'feedback']


class CustomStatus(admin.ModelAdmin):
    model = Status
    list_display = ['name', 'for_doctor', 'for_payment', 'for_chat', 'for_sickness']


new_site.register(User, CustomUser)
new_site.register(DiagnosisPeriod, CustomPeriod)
new_site.register(Status, CustomStatus)
new_site.register(Role)
new_site.register(Sickness, CustomSickness)
new_site.register(Medication, CustomMedication)
new_site.register(MedicalRecord, CustomMedicalRecord)
new_site.register(RealTimeChat, CustomRealTimeChat)
new_site.register(MedicalRecordDetail, CustomMedicalRecordDetail)
new_site.register(Payment, CustomPayment)
new_site.register(Evaluation, CustomEvaluation)
# new_site.register(Status)