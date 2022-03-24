from django.shortcuts import render, redirect

from main import trading_views
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
    memberlist = []
    # owner
    totalPortValue = 0
    player = league.owner
    playerPortfolio = LeaguePortfolio.objects.filter(owner = player,league = league)[0]
    playerHoldings = [holding for holding in LeagueHolding.objects.filter(owner = player,league = league)]
    for holding in playerHoldings:
        totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
    totalPortValue +=  playerPortfolio.balance
    player.league_portfolio_value = totalPortValue
    memberlist.append(player)
    # all other members    
    for participant in league.participants.all():
        playerPortfolio = LeaguePortfolio.objects.filter(owner = participant,league = league)[0]
        playerHoldings = [holding for holding in LeagueHolding.objects.filter(owner = participant,league = league)]
        totalPortValue = 0
        for holding in playerHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        totalPortValue +=  playerPortfolio.balance
        participant.league_portfolio_value = totalPortValue
        memberlist.append(participant)
    memberlist.sort(key = lambda x: x.league_portfolio_value)
    memberlist = memberlist[::-1]
    leagueSizeBig = True
    if len(memberlist) > 3:
        winner = memberlist[0]
        del memberlist[0]
        silver = memberlist[0]
        del memberlist[0]
        bronze = memberlist[0]
        del memberlist[0]
    else:
        leagueSizeBig = False
        winner = None
        silver = None
        bronze = None

    return render(request, "leagues/league_leaderboard.html", {
        "league": league,
        "league_size": leagueSizeBig,
        "members": memberlist,
        "gold": winner,
        "silver": silver,
        "bronze": bronze,
        })

def league_asset_listing_page(request, league_name, ticket):
    request.league = league_name
    return trading_views.asset_page(request, ticket)