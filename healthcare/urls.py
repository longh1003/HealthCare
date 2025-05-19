
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('medical-records', views.MedicalRecordViewSet, basename='med-record')
router.register('online-chat', views.ChatViewSet, basename='online-chat')


urlpatterns = [
    path('', include(router.urls))
]