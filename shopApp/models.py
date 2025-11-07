from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class ShopDetailsModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)

class ShopPermissionsModel(models.Model):
    shop = models.ForeignKey(ShopDetailsModel, on_delete=models.CASCADE)
    email = models.EmailField()
    
    class Meta:
        unique_together = ['shop', 'email']

    @property
    def is_admin(self):
        return True

    