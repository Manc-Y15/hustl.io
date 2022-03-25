from django.shortcuts import render, redirect

from main import trading_views
from .models import Stock, Profile, Portfolio, Holding, User, League, LeaguePortfolio, LeagueHolding
from .leagues import create_league, add_user,remove_user 
import random
import json
from datetime import datetime
import calendar
from .constants import *
from .main_views import error_view

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
            return redirect(f'/leagues/{newleagueName}')
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
        "members": memberlist[:37],
        "gold": winner,
        "silver": silver,
        "bronze": bronze,
        })

def league_asset_listing_page(request, league_name, ticket):
    return trading_views.asset_page(request, ticket, league_name)

def league_portfolio(request,league_name):
    league = League.objects.filter(name = league_name)[0]
    userHoldings = [holding for holding in LeagueHolding.objects.filter(owner = request.user,league = league)]
    for holding in userHoldings:
        cols = holding.stock_id.display_colour.split(' ') # Get gradient split for each held stock
        holding.stock_id.col1 = cols[0].split('(')[1][:-1]
        holding.stock_id.col2 = cols[1].split('(')[1][:-1]
        holding.stock_id.balance = (round((holding.stock_id.current_price * holding.amount),2))

    # number of trades    
    portID = LeaguePortfolio.objects.filter(owner =request.user,league = league)[0]
    userTrades = 1

    # total portfolio value
    totalPortValue = 0
    for holding in userHoldings:
        totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
    portfolio = LeaguePortfolio.objects.filter(owner = request.user,league = league)[0]
    totalPortValue +=  portfolio.balance
    portValue = f"${totalPortValue:,}"
    userProfit = f"${(totalPortValue  - league.starting_balance):,}"


    lastTrade = None

    # getting data for the line graph
    historical_balance = json.loads(portfolio.bal_hist)['history']
    if len(historical_balance) > 8 and historical_balance[8]['oldData'] > historical_balance[len(historical_balance)-1]['oldData']:
            portfolio.pos = False
    else: portfolio.pos = True

    # Value history graph gradient colours
    portfolio.col1 = "--turquoise"
    portfolio.col2 = "--amethyst"

    raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_balance]
    # Date for each price datum in historical value graph
    dates = []
    for raw in raw_day_dates:
        split = raw.split('-')
        dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        
    value_history = [f"{datum['oldData']:.2f}" for datum in historical_balance]
    if len(dates) > 7: 
        value_history = value_history[7:]
        dates = dates[7:]

    # asset pie chart
    ticket_list = []
    data_list = []
    sorting_list = [['Cash',float(round((portfolio.balance / totalPortValue ) * 100 ,2))]]
    for holding in userHoldings:
        if holding.amount > 0:
            sorting_list.append([])
            sorting_list[-1].append(holding.stock_id.ticket)
            sorting_list[-1].append( float( round((holding.stock_id.balance / totalPortValue ) * 100,2)))
            # Get percentage of total value
    sorting_list.sort(key = lambda x: x[1])
    for item in sorting_list:
        ticket_list.append(item[0])
        data_list.append(item[1])

    colour_list = CIRCULAR_COLOUR_LIST

    asset_data = {'tickets': ticket_list ,'data' :data_list,'colours': colour_list }
    return render(request, "trading/portfolio.html",{
        'numOfTrades': userTrades,
        'rankRegional': '13',
        'rankOverall': '78',
        'totalProfit': userProfit,
        'totalPortValue': portValue,
        'lastTraded': lastTrade,
        'userstocks': userHoldings,
        'portfolio': portfolio,
        'valueData':str({
                "value_history": value_history,
                "dates": dates
            }),
        'assetData':str(asset_data)
    })