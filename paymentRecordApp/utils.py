
from django.db import models
from  .models import CustomerBalanceModel

def get_shop_balance(shop_id):
    balance_details = CustomerBalanceModel.objects.filter(
        shop__id=shop_id
        ).aggregate(
            overall_balance = models.Sum('balane_amount')
        )
    return {
        "shop_balance" : balance_details["overall_balance"]
    }