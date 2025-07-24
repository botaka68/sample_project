from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    org = models.CharField(max_length=100, blank=True)
    invite_code = models.CharField(max_length=32, blank=False)
    

    def __str__(self):
        return  self.username


class Organization(models.Model):
    organization = models.CharField(max_length=32)
    phantom_server = models.CharField(max_length=100)
    auth_token = models.CharField(max_length=64)
    label = models.CharField(max_length=32)
    invite_code = models.CharField(max_length=32)
    description = models.TextField()
    
    def __str__(self):
        return self.organization


class InviteCode(models.Model):
    organization_id = models.CharField(max_length=32)
    invite_code = models.CharField(max_length=32)
    
    def __str__(self):
        return self.organization_id