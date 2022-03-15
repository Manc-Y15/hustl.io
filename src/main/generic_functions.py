from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Stock,Profile,Portfolio,Holding,User
    
    
def getPortfolioValue(player):   
    userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
    player.portfolio_value = player.portfolio.balance
    for holding in userHoldings:
        player.portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
    return(player.portfolio_value)