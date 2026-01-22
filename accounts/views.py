from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from utils.token import email_token_generator
from utils.pagination import StandardResultsSetPagination
from Luli.utils import format_errors
from .serializers import RegisterSerializer, UserSerializer, UserListSerializer, UserProfileSerializer, CompleteUserProfileSerializer, ExtendedUserProfileSerializer, AddressSerializer, AppointmentSerializer, AppointmentCreateSerializer
from .models import Address, UserProfile, Appointment

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # Open to all users

    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({"detail": "Username/email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username_or_email, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if user.status != 1:
            return Response({"detail": "User is inactive or deleted."}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "id": user.id,
            "loginname": user.loginname,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Token error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
  

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created. Check your email to verify."}, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

class EmailVerifyAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        if not email_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.status = 1  # Activate user
        user.save()
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


class UserListAPIView(APIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                user = User.objects.get(pk=pk)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            filters = dict(request.GET.items())
            users = User.objects.exclude(status=3) 
            page_param = filters.pop('page', None)  # Remove page from filters to avoid filtering by page
            if filters:
                users = users.filter(**filters)
            
            # Pagination - only if page parameter is provided
            if page_param is not None:
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(users, request)
                if page is not None:
                    serializer = UserListSerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
            
            serializer = UserListSerializer(users, many=True)
            return Response({"status": 200, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "User ID is required for update."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "User ID is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.status = 3
        user.save()

        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)



# User Profile Views
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = CompleteUserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        
        serializer = CompleteUserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


# Extended User Profile Views
class ExtendedUserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ExtendedUserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ExtendedUserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ExtendedUserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


# Address Views
class AddressListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('address_type'):
            filters['address_type'] = request.query_params.get('address_type')
        
        if request.query_params.get('is_default'):
            filters['is_default'] = request.query_params.get('is_default').lower() == 'true'
        
        if request.query_params.get('is_billing'):
            filters['is_billing'] = request.query_params.get('is_billing').lower() == 'true'
        
        if request.query_params.get('is_shipping'):
            filters['is_shipping'] = request.query_params.get('is_shipping').lower() == 'true'
        
        if request.query_params.get('city'):
            filters['city__icontains'] = request.query_params.get('city')
        
        if request.query_params.get('state'):
            filters['state__icontains'] = request.query_params.get('state')
        
        queryset = Address.objects.filter(user=request.user)
        if filters:
            queryset = queryset.filter(**filters)
        
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            serializer = AddressSerializer(address)
            return Response(serializer.data)
        except Address.DoesNotExist:
            return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Address.DoesNotExist:
            return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            address.delete()
            return Response({'message': 'Address deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Address.DoesNotExist:
            return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)


# Appointment Views
class AppointmentListView(APIView):
    permission_classes = [AllowAny]  # Allow both authenticated and non-authenticated users
    
    def get(self, request):
        """List all appointments (filtered by user if authenticated)"""
        if request.user.is_authenticated:
            appointments = Appointment.objects.filter(user=request.user)
        else:
            # For non-authenticated users, require email filter
            email = request.query_params.get('email')
            if not email:
                return Response(
                    {'message': 'Email parameter is required for non-authenticated users'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            appointments = Appointment.objects.filter(email=email)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        
        # Order by appointment date
        appointments = appointments.order_by('-appointment_date', '-created_at')
        
        serializer = AppointmentSerializer(appointments, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new appointment"""
        serializer = AppointmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # If user is authenticated, link the appointment to the user
            appointment = serializer.save()
            if request.user.is_authenticated:
                appointment.user = request.user
                appointment.save()
            
            # Return full appointment details
            appointment_serializer = AppointmentSerializer(appointment, context={'request': request})
            return Response(appointment_serializer.data, status=status.HTTP_201_CREATED)
        
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class AppointmentDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Allow both authenticated and non-authenticated users
    
    def get(self, request, pk):
        """Retrieve a specific appointment"""
        try:
            appointment = Appointment.objects.get(pk=pk)
            
            # Check permissions
            if request.user.is_authenticated:
                if appointment.user != request.user:
                    return Response(
                        {'error': 'You do not have permission to view this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                # For non-authenticated users, require email verification
                email = request.query_params.get('email')
                if not email or appointment.email != email:
                    return Response(
                        {'error': 'Email verification required to view this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = AppointmentSerializer(appointment, context={'request': request})
            return Response(serializer.data)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """Update an appointment"""
        try:
            appointment = Appointment.objects.get(pk=pk)
            
            # Check permissions
            if request.user.is_authenticated:
                if appointment.user != request.user:
                    return Response(
                        {'error': 'You do not have permission to update this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                # For non-authenticated users, require email verification
                email = request.data.get('email') or request.query_params.get('email')
                if not email or appointment.email != email:
                    return Response(
                        {'error': 'Email verification required to update this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = AppointmentSerializer(appointment, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = '; '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        """Cancel/Delete an appointment"""
        try:
            appointment = Appointment.objects.get(pk=pk)
            
            # Check permissions
            if request.user.is_authenticated:
                if appointment.user != request.user:
                    return Response(
                        {'error': 'You do not have permission to delete this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                # For non-authenticated users, require email verification
                email = request.data.get('email') or request.query_params.get('email')
                if not email or appointment.email != email:
                    return Response(
                        {'error': 'Email verification required to delete this appointment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            appointment.delete()
            return Response({'message': 'Appointment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


