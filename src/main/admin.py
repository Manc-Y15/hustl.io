from django.contrib import admin
from .models import Stock, Portfolio, Holding, Profile, Transaction, League, LeagueHolding, LeaguePortfolio

admin.site.register(Stock)
admin.site.register(Portfolio)
admin.site.register(Holding)
admin.site.register(Profile)
admin.site.register(Transaction)
admin.site.register(League)
admin.site.register(LeagueHolding)
admin.site.register(LeaguePortfolio)