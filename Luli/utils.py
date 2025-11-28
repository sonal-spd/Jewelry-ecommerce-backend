from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
from rest_framework.response import Response


class EmailTokenGenerator:
    """Custom token generator for email verification"""
    
    def make_token(self, user):
        """Generate token for user"""
        return default_token_generator.make_token(user)
    
    def check_token(self, user, token):
        """Check if token is valid for user"""
        return default_token_generator.check_token(user, token)


# Create instance
email_token_generator = EmailTokenGenerator()


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


def format_errors(errors):
    """Format serializer errors into a list of strings"""
    formatted_errors = []
    for field, msgs in errors.items():
        for msg in msgs:
            # Don't add field prefix for non_field_errors
            if field == 'non_field_errors':
                formatted_errors.append(str(msg))
            else:
                formatted_errors.append(f"{field}: {msg}")
    return {"errors": formatted_errors} 

    