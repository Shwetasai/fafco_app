from rest_framework import status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .serializers import CustomerSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken,TokenError
import json
import base64
from .serializers import CustomerSerializer, UserLoginSerializer 
from .serializers import ProfileSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.hashers import check_password
from base64 import urlsafe_b64encode, urlsafe_b64decode
from .serializers import PasswordResetSerializer, SetNewPasswordSerializer,UpdatePasswordSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str


class RegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        phone = request.data.get('phone')
        email = request.data.get('email')
        password = request.data.get('password')
        customer_type = request.data.get('customer_type')

        if not name or not email or not password or not customer_type:
            return Response({'error': 'Name, email, password, and customer_type are required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_users = CustomUser.objects.filter(email=email)
        if existing_users.exists():
            return Response({'error': 'Email already exists. You may proceed to login or reset your password if necessary.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = {
            'name': name,
            'email': email,
            'customer_type': customer_type,
            'password': password
        }

        if phone:
            user_data['phone'] = phone

        encoded_user_data = base64.urlsafe_b64encode(json.dumps(user_data).encode()).decode()
        verification_link = f"{request.scheme}://{request.get_host()}/api/users/verify/?data={encoded_user_data}"

        send_mail(
            subject='Verify your email',
            message=f"Click the link to verify your email and complete registration: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({
            "message": "Verification email sent. Please check your email to complete registration.",
        }, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        encoded_user_data = request.query_params.get('data')
        if not encoded_user_data:
            return Response({"error": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        decoded_user_data = json.loads(base64.urlsafe_b64decode(encoded_user_data).decode())
        email = decoded_user_data["email"]
        name = decoded_user_data["name"]
        password = decoded_user_data["password"]
        customer_type = decoded_user_data["customer_type"]

        user_kwargs = {
            'email': email,
            'name': name,
            'password': password,
            'customer_type': customer_type,
        }

        if 'phone' in decoded_user_data:
            user_kwargs['phone'] = decoded_user_data['phone']

        user = CustomUser.objects.create_user(**user_kwargs)
        user.is_email_verified = True
        user.save()

        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        login_serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'email': user.email
            }, status=status.HTTP_200_OK)
            
        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, current_dealer=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, current_dealer=user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(ProfileSerializer(updated_profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, current_dealer=user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(ProfileSerializer(updated_profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, current_dealer=user)
        profile.delete()
        return Response({"message": "Profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UserLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            authorization_header = request.headers.get("Authorization")
            if not authorization_header or not authorization_header.startswith("Bearer "):
                return Response({"error": "Invalid Authorization header format."}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = authorization_header.split()[1]  # Extract access token from Authorization header

            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except InvalidToken:
            return Response({"error": "Invalid token provided."}, status=status.HTTP_401_UNAUTHORIZED)

        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": "Failed to logout."}, status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UpdatePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password successfully changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.BASE_URL}api/users/password-reset/{uid}/{token}/"

        send_mail(
            'Password Reset Request',
            f'Please click the following link to reset your password: {reset_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return Response({'message': 'Password reset link sent successfully.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return Response({'message': 'Token is valid.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            if len(new_password) < 6:
                return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)