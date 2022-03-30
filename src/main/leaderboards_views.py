from django.shortcuts import render, redirect
from .models import Stock,Profile,Portfolio,Holding,User
from .generic_functions import get_user_leagues
from .constants import *
from django.contrib.auth.decorators import login_required


@login_required
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
    return render(request, "leaderboards/leaderboard.html", {
        "users": userlist[:37],
        "gold": winner,"silver": silver,
        "bronze": bronze,
        'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
        })

def leaderboard_view_friends(request):
    userlist = []
    # get friends
    print(request.user.friends.all())

    for profile in request.user.friends.all():
        player = profile.user
        userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
        totalPortValue = 0
        for holding in userHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        totalPortValue +=  player.portfolio.balance
        player.portfolio_value = totalPortValue

        if player in request.user.profile.friends.all(): player.is_friend = True
        else: player.is_friend = False
        userlist.append(player)
    print(userlist)
    # add you to the list
    userHoldings = [holding for holding in Holding.objects.filter(owner = request.user)]
    totalPortValue = 0
    for holding in userHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
    totalPortValue +=  request.user.portfolio.balance
    request.user.portfolio_value = totalPortValue
    request.user.is_friend = False
    userlist.append(request.user)
    print(userlist)    
    # sort the list
    userlist.sort(key = lambda x: x.portfolio_value)
    userlist = userlist[::-1]
    print(userlist)
    # check if you have enough friends for gold, silver etc
    SizeBig = True
    if len(userlist) > 3:
        winner = userlist[0]
        del userlist[0]
        silver = userlist[0]
        del userlist[0]
        bronze = userlist[0]
        del userlist[0]
        print(userlist)
    else:
        SizeBig = False
        winner = None
        silver = None
        bronze = None
    return render(request, "leaderboards/friend_leaderboard.html", {
        "users": userlist[:37],
        "gold": winner,"silver": silver,
        "bronze": bronze,
        "board_size": SizeBig,
        'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
        })