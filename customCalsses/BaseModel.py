

from django.db import models
from shopApp.models import ShopDetailsModel

class BaseModel(models.Model):
    shop  = models.ForeignKey(ShopDetailsModel, on_delete=models.CASCADE)

    class Meta:
        abstract = True