from django.db import models
from django.contrib.auth.models import User

'''
Stock Data Class
- Stock ID
- Ticket
- Name
- Desc (?)
- Current Price
- Current DateTime
- Historical
'''

class StockData(models.Model):
    ticket = models.CharField(max_length=5)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_datetime = models.DateTimeField()
    historical = models.TextField()

    def __str__():
        print(f"{ticket} {name} {current_price} at {current_datetime}")