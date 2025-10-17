from django.db import models

from shopApp.models import  ShopDetailsModel

class CustomerDetailsModel(models.Model):
    shop =  models.ForeignKey(ShopDetailsModel, on_delete=models.CASCADE)
    first_name =  models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=20)