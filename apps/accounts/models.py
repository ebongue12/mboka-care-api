import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, default='PATIENT')
    
    username = None
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
