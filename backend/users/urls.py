from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import (RegistrationAPIView, UserLoginView, ProfileAPIView,UserLogoutView,
 UpdatePasswordView,PasswordResetRequestView,PasswordResetConfirmView)

urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('verify/', RegistrationAPIView.as_view(), name='verify_user'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('update-password/',UpdatePasswordView.as_view(), name='update_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   ]


