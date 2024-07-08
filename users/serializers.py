from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import Profile, CustomUser
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import send_mail

class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)


    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'password', 'customer_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class TokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials', code='authorization')
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'id': user.id,
            'email': user.email,
        }
        

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None:
                raise serializers.ValidationError('Invalid credentials', code='authorization')
        
            refresh = RefreshToken.for_user(user)
            attrs['user'] = user
            attrs['id'] = user.id
            attrs['email'] = user.email
            attrs['access_token'] = str(refresh.access_token)
            attrs['refresh_token'] = str(refresh)
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    current_dealer = CustomerSerializer()
    previous_dealer = CustomerSerializer()
    owner_phone = PhoneNumberField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'address', 'state', 'country', 'zip_code', 'created_at',
            'current_dealer', 'previous_dealer',
            'owner_phone', 'owner_email', 'is_active', 'medallion'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        address = data.get('address')
        state = data.get('state')
        country = data.get('country')

        # Check if profile with same address, state, and country already exists
        if Profile.objects.filter(address=address, state=state, country=country).exists():
            raise serializers.ValidationError("This address is already claimed.")
        return data
        
    def create(self, validated_data):
        current_dealer_data = validated_data.pop('current_dealer')
        previous_dealer_data = validated_data.pop('previous_dealer')
        owner_phone_data = validated_data.pop('owner_phone')

        if not owner_phone_data:
            raise serializers.ValidationError("Owner phone number is required.")

        current_dealer = CustomUser.objects.create(**current_dealer_data)
        previous_dealer = CustomUser.objects.create(**previous_dealer_data)

        profile = Profile.objects.create(
            current_dealer=current_dealer,
            previous_dealer=previous_dealer,
            owner_phone=owner_phone_data,
            **validated_data
        )
        
        return profile

    def update(self, instance, validated_data):
        current_dealer_data = validated_data.pop('current_dealer', None)
        previous_dealer_data = validated_data.pop('previous_dealer', None)

        if current_dealer_data:
            current_dealer_serializer = CustomerSerializer(instance.current_dealer, data=current_dealer_data, partial=True)
            if current_dealer_serializer.is_valid():
                current_dealer_serializer.save()

        if previous_dealer_data:
            previous_dealer_serializer = CustomerSerializer(instance.previous_dealer, data=previous_dealer_data, partial=True)
            if previous_dealer_serializer.is_valid():
                previous_dealer_serializer.save()

        updated_instance = super().update(instance, validated_data)
        
        return updated_instance




class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/update_password/{uid}/{token}/"
        send_mail(
            "Password Reset Request",
            f"Click the link below to reset your password:\n{reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = CustomUser.objects.get(pk=uid)
            if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
                raise serializers.ValidationError("Invalid token.")
            user.set_password(attrs['new_password'])
            user.save()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user.")
        return attrs