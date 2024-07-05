from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractBaseUser):
    Dealer = 1
    Homeowner = 2

    CUSTOMER_TYPES = [
        (Dealer, 'Dealer'),
        (Homeowner, 'Homeowner'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, null=False, blank=False)
    phone = PhoneNumberField(null=False, blank=False)
    email = models.EmailField(('email address'), unique=True, null=False, blank=False)
    customer_type = models.PositiveSmallIntegerField(choices=CUSTOMER_TYPES)
    fbid = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'customer_type']

    def __str__(self):
        return self.email

    def can_login(self):
        return self.is_active

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255) 
    country = models.CharField(max_length=255)  
    zip_code = models.CharField(max_length=20, default='00000')
    created_at = models.DateTimeField(auto_now_add=True)
    current_dealer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='current_dealer_profile')
    previous_dealer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='previous_dealer_profile')
    owner_phone = PhoneNumberField(null=False, blank=False)
    owner_email = models.EmailField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    medallion = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile - {self.address}"

    def save(self, *args, **kwargs):
        self.address = self.address.replace(' ', '_')
        super().save(*args, **kwargs)

