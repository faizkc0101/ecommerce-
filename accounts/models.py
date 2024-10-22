from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_field = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.user.email

