
from django.urls import path
from .views import *

urlpatterns = [
    # Authentication
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/', EmailVerifyAPIView.as_view(), name='verify_email'),
    
    # User Management
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserListAPIView.as_view(), name='user-detail'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/extended/', ExtendedUserProfileView.as_view(), name='extended-user-profile'),
    
    # Addresses
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    
    # Appointments
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
  
]
