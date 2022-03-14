from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from .models import Stock,Profile,Portfolio,Holding,User

def leaderboard_view(request):
    userlist = []
    for player in User.objects.all():
        userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
        totalPortValue = 0
        for holding in userHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        totalPortValue +=  player.portfolio.balance
        player.portfolio_value = totalPortValue
        userlist.append(player)
    winner = userlist[0]
    del userlist[0]
    silver = userlist[0]
    del userlist[0]
    bronze = userlist[0]
    del userlist[0]
    return render(request, "leaderboards/leaderboard.html", {"users": userlist, "gold": winner,"silver": silver,"bronze": bronze})