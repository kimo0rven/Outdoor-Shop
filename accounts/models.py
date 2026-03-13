from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    is_customer = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)