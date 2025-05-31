from rest_framework import pagination

class MedicalRecordPaginator(pagination.PageNumberPagination):
    page_size = 5

class MedicalRecordDetailPaginator(pagination.PageNumberPagination):
    page_size = 5

class DiagnosisPeriodPaginator(pagination.PageNumberPagination):
    page_size = 5