from django.core.paginator import Paginator
from rest_framework.response import Response


class Pagination:
    """Custom pagination class"""
    
    def __init__(self, page_size=20):
        self.page_size = page_size
    
    def paginate_queryset(self, queryset, request):
        """Paginate queryset"""
        page = request.query_params.get('page', 1)
        paginator = Paginator(queryset, self.page_size)
        return paginator.get_page(page)
    
    def get_paginated_response(self, data):
        """Return paginated response"""
        return Response(data)
