from django.shortcuts import render, redirect
from .models import Stock, Profile, Portfolio, Holding, User, League, LeaguePortfolio, LeagueHolding
from .leagues import create_league, add_user,remove_user 
import random
def view_leagues(request):
    allLeagues = list(League.objects.filter(owner = request.user))
    for league in League.objects.exclude(owner = request.user):
        if request.user in league.participants.all():
            allLeagues.append(league)
    return render(request, 'leagues/leagues.html', {
        'userLeagues': allLeagues,
    })
        

def create_league_view(request):
    errors = []
    if request.method == "POST":
        newleagueName = request.POST.get("league_name", "")
        startBal = request.POST.get("league_start_bal", "")
        icon = random.randint(0,20)
        created = create_league(request.user, newleagueName, startBal, icon)
        
        if created:
            return render(request, f'leagues/{newleagueName}')
        else:
            errors.append(created[1])

    return render(request, 'leagues/league_creation.html', {
        'errors': errors,
    })

def league_leaderboard(request,league_name):
    league = League.objects.filter(name = league_name)[0]
    print(league.name)
    print(league.participants.all())
    # how do i pass league into this function
    memberlist = []
    for participant in league.participants.all():
        playerHoldings = [holding for holding in LeagueHolding.objects.filter(owner = participant,league = league)]
        totalPortValue = 0
        for holding in playerHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        totalPortValue +=  participant.leagueportfolio.balance
        participant.league_portfolio_value = totalPortValue
        memberlist.append(participant)
    memberlist.sort(key = lambda x: x.league_portfolio_value)
    userlist = memberlist[::-1]
    
    winner = memberlist[0]
    del memberlist[0]
    silver = memberlist[0]
    del memberlist[0]
    bronze = memberlist[0]
    del memberlist[0]
    return render(request, "leaderboards/leaderboard.html", {
        "league": league,
        "members": memberlist,
        "gold": winner,
        "silver": silver,
        "bronze": bronze,
        })