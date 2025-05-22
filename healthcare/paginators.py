from rest_framework import pagination

class MedicationPaginator(pagination.PageNumberPagination):
    page_size = 2