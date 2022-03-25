from django.shortcuts import render, redirect
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

        if player in request.user.profile.friends.all(): player.is_friend = True
        else: player.is_friend = False
        userlist.append(player)
    userlist.sort(key = lambda x: x.portfolio_value)
    userlist = userlist[::-1]
    
    winner = userlist[0]
    del userlist[0]
    silver = userlist[0]
    del userlist[0]
    bronze = userlist[0]
    del userlist[0]
    return render(request, "leaderboards/leaderboard.html", {"users": userlist[:37], "gold": winner,"silver": silver,"bronze": bronze})