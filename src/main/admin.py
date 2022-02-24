from django.contrib import admin
from .models import StockData, Portfolio, Holding, Profile

admin.site.register(StockData)
admin.site.register(Portfolio)
admin.site.register(Holding)
admin.site.register(Profile)