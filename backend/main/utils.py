from rest_framework.pagination import PageNumberPagination


class CustomSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'limit'
    max_page_size = 10000
