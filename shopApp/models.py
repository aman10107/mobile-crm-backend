from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class ShopDetailsModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)