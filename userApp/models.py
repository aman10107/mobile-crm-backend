from django.db import models

# Create your models here.
from django.contrib.auth.models import  User
from shopApp.models import ShopDetailsModel

class UserDetailsModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_create_shops_count = models.IntegerField(default=0)

    def canCreateShop(self):
        shops = ShopDetailsModel.objects.filter(owner=self.user)
        return self.can_create_shops_count <= shops.count