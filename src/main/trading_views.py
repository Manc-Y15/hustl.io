from django.shortcuts import render, redirect, HttpResponse
from .models import Stock, Holding, Portfolio, Transaction,User, League, LeagueHolding
from django.contrib.auth.decorators import login_required
from .transactions import user_buy, user_sell_all
from random import randint, choice
import json
from datetime import datetime
import calendar
from .generic_functions import getPortfolioValue, percentage_change, get_user_leagues
from .constants import *
from .main_views import error_view

# asset_page_form (view func)
# Only used for receiving post request from asset_page; validates transaction and returns partial HTML response.
def asset_page_form(request):
    if request.method == "POST":
        form = {}
        transaction = {}
        league = request.POST.get("league", "")
        if request.POST.get("transaction", "") == "sellall": # sellall needs to be handled separately 
            stock = Stock.objects.filter(ticket =  request.POST.get("ticket", ""))[0] # find stock in db
            if league == "global":
                if Holding.objects.filter(owner = request.user, stock_id = stock).exists():
                    holding =  Holding.objects.filter(owner =  request.user, stock_id = stock)[0]
                    transaction['amount'] = holding.amount * stock.current_price

                    order = user_sell_all(request.user, request.POST.get("ticket", "")) # autos to global league

                    if order[0]:
                        form['success'] = True
                    else:
                        transaction['error'] = order[1] # Error msg to send back in HTML
                        form['success'] = False
                    transaction['is_buy'] = False
                    transaction['stock_id'] = request.POST.get("ticket", "")
                else:
                    # Fail if user has no holding in stock
                    form['success'] = False
            else:
                leagueobj = League.objects.filter(name = league)[0]
                if LeagueHolding.objects.filter(owner = request.user, stock_id = stock, league = leagueobj).exists():
                    holding =  LeagueHolding.objects.filter(owner =  request.user, stock_id = stock, league = leagueobj)[0]
                    transaction['amount'] = holding.amount * stock.current_price

                    order = user_sell_all(request.user, request.POST.get("ticket", ""), league)

                    if order[0]:
                        form['success'] = True
                    else:
                        transaction['error'] = order[1] # Error msg to send back in HTML
                        form['success'] = False
                    transaction['is_buy'] = False
                    transaction['stock_id'] = request.POST.get("ticket", "")
                else:
                    # Fail if user has no holding in stock
                    form['success'] = False
            
        else: # Must be either buy or sell
            transaction = {
                "is_buy": True if (request.POST.get("transaction", "") == "buy") else False,
                "stock_id": request.POST.get("ticket", ""), 
                "amount": request.POST.get("amount", "")
            }
            order = user_buy(request.user, transaction['is_buy'], transaction['stock_id'], float(transaction['amount']), league)
            if order[0]: # if order is success
                form['success'] = True
            else:
                transaction['error'] = order[1] # error msg
                form['success'] = False
        stock = Stock.objects.filter(ticket=request.POST.get("ticket", ""))[0]
        cols = stock.display_colour.split(' ') # Split off gradient colours
        stock.col1 = cols[0].split('(')[1][:-1]
        stock.col2 = cols[1].split('(')[1][:-1]

        return render(request, 'trading/stock_listing_response.html', {
            "form": form,
            "transaction": transaction,
            "stock": stock,
            'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})
        
# asset_page (view function)
# Main page for a stock listing.
# ticket = The stock you are requesting to see.
def asset_page(request, ticket, league_name="global"):
    if league_name != "global" and not request.user.is_authenticated:
        return error_view(request, error="You need to be logged in to view your leagues.")

    if league_name != "global":
        if len(League.objects.filter(name=league_name)) == 0:
            return error_view(request, error="This league doesn't exist.")
        
        leagueobj = League.objects.filter(name = league_name)[0]
        if not (request.user in leagueobj.participants.all() or leagueobj.owner == request.user):
                return error_view(request, error="You are not in this league.")


    query_matches = Stock.objects.filter(ticket=ticket)
    if len(query_matches) != 1:
        # TODO: Change to error page
        return render(request, 'home.html', {})
    else:
        stock = query_matches[0]
        historical_prices = json.loads(stock.historical)['history'] # Get historical stock data
        if historical_prices[8]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            # Compare with price from 7 days ago
            stock.pos = False
        else: stock.pos = True

        cols = stock.display_colour.split(' ') # Gradient colour split
        stock.col1 = cols[0].split('(')[1][:-1]
        stock.col2 = cols[1].split('(')[1][:-1]

        raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_prices]
        # Get dates for each price datum in historical_prices
        dates = []
        for raw in raw_day_dates:
            split = raw.split('-')
            dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        
        value_history = [f"{datum['oldData']:.2f}" for datum in historical_prices]
        if len(dates) > 7: 
            value_history = value_history[7:]
            dates = dates[7:]
    if request.user.is_authenticated:
        # Get transactions for activity feed
        transactions = []
        thisStock = Stock.objects.filter(ticket=ticket)[0]
        allTransactions = Transaction.objects.filter(stock_id = thisStock)
        activityFeed = []
        transactions = []
        for transac in allTransactions:
            if transac.portfolio_id.owner == request.user or transac.portfolio_id.owner in request.user.profile.friends.all():
                activityFeed.append(transac)

        for transac in activityFeed:
            new_transacaction = []
            if transac.portfolio_id.owner.username == request.user.username:
                new_transacaction.append("You")
            else:
                new_transacaction.append(transac.portfolio_id.owner.username)

            new_transacaction.append('bought' if transac.buy else 'sold')
            new_transacaction.append(round(transac.buy_price * transac.volume,2))
            new_transacaction.append(transac.stock_id.ticket)
            new_transacaction.append(transac.buy_price)
            new_transacaction.append(transac.time)
            transactions.append(new_transacaction)
        transactions.reverse()
        transactions = transactions[:6]
    else:
        transactions = []

    
    return render(request, 'trading/stock_listing.html', {
        'stock': stock,
        'transactions': transactions,
        'data': str({
            "value_history": value_history,
            "dates": dates
        }),
        'league': league_name,
        'league_info': {'current_league': league_name, 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
    }
    )


# asset_list_page (view func)
# List of all stocks available & price information
def asset_list_page(request, league_name="global"):
    if league_name != "global" and not request.user.is_authenticated:
        return error_view(request, error="You need to be logged in to view your leagues.")

    if league_name != "global":
        if len(League.objects.filter(name=league_name)) == 0:
            return error_view(request, error="This league doesn't exist.")
        
        leagueobj = League.objects.filter(name = league_name)[0]
        if not (request.user in leagueobj.participants.all() or leagueobj.owner == request.user):
                return error_view(request, error="You are not in this league.")
    
    


    stocks = [stock for stock in Stock.objects.all()]
    positive = {}
    for stock in stocks:
        historical_prices = json.loads(stock.historical)['history']
        if historical_prices[7]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            # Compare current with 7 day old price
            stock.pos = False
        else: stock.pos = True

        cols = stock.display_colour.split(' ') # Gradient colour split
        stock.col1 = cols[0]
        stock.col2 = cols[1]
        #stock.background = choose_background(stock)
    return render(request, "trading/stock_list.html", {
        'stocks': stocks,
        'league': league_name,
        'league_info': {'current_league': league_name, 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
    })

# portfolio_view (view func)
# Requires user to be logged in.
# Displays all relevant information about a user's portfolio db record.
@login_required
def portfolio_view(request):
    userHoldings = [holding for holding in Holding.objects.filter(owner = request.user)]
    for holding in userHoldings:
        cols = holding.stock_id.display_colour.split(' ') # Get gradient split for each held stock
        holding.stock_id.col1 = cols[0].split('(')[1][:-1]
        holding.stock_id.col2 = cols[1].split('(')[1][:-1]
        holding.stock_id.balance = (round((holding.stock_id.current_price * holding.amount),2))

    # number of trades    
    portID = Portfolio.objects.filter(owner =request.user)[0]
    userTrades = 0
    for trades in Transaction.objects.filter(portfolio_id = portID):
        userTrades += 1

    # total portfolio value
    totalPortValue = 0
    for holding in userHoldings:
        totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
    portfolio = Portfolio.objects.filter(owner = request.user)[0]
    totalPortValue +=  portfolio.balance
    portValue = f"${totalPortValue:,}"
    userProfit = f"${(totalPortValue  - 50000):,}"

    # Last trade query & colour setting
    if len(Transaction.objects.filter(portfolio_id = portID)) > 0:
        lastTrade = Transaction.objects.filter(portfolio_id = portID).last().stock_id
    
        cols = lastTrade.display_colour.split(' ')
        lastTrade.col1 = cols[0].split('(')[1][:-1]
        lastTrade.col2 = cols[1].split('(')[1][:-1]
    else:
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
        'rankOverall': request.user.portfolio.leaderboard_ranking,
        'totalProfit': userProfit,
        'totalPortValue': portValue,
        'lastTraded': lastTrade,
        'userstocks': userHoldings,
        'portfolio': portfolio,
        'valueData':str({
                "value_history": value_history,
                "dates": dates
            }),
        'assetData':str(asset_data),
        'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
    })

# other_user_portfolio (view func)
# Duplicate of portfolio but with some data removed (asset values)
def other_user_portfolio(request,name):
    player = User.objects.filter(username = name)[0]
    player.value = getPortfolioValue(player)
    if len(Transaction.objects.filter(portfolio_id = player.portfolio)) > 0:
        lastTrade = Transaction.objects.filter(portfolio_id = player.portfolio).last().stock_id
    
        cols = lastTrade.display_colour.split(' ')
        lastTrade.col1 = cols[0].split('(')[1][:-1]
        lastTrade.col2 = cols[1].split('(')[1][:-1]
    else:
        lastTrade = None
    name = name
    userTrades = len(Transaction.objects.filter(portfolio_id = player.portfolio))
    portfolio = player.portfolio
    historical_balance = json.loads(portfolio.bal_hist)['history']
    if len(historical_balance) > 8 and historical_balance[8]['oldData'] > historical_balance[len(historical_balance)-1]['oldData']:
            portfolio.pos = False
    else: portfolio.pos = True

    portfolio.col1 = "--turquoise"
    portfolio.col2 = "--amethyst"

    raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_balance]
    dates = []
    for raw in raw_day_dates:
        split = raw.split('-')
        dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        
    value_history = [f"{datum['oldData']:.2f}" for datum in historical_balance]
    if len(dates) > 7: 
        value_history = value_history[7:]
        dates = dates[7:]
    userFriend = False
    if player in request.user.profile.friends.all():
        userFriend = True
        # asset graph 
        ticket_list = []
        data_list = []
        userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
        sorting_list = [['Cash',float(round((portfolio.balance / player.value ) * 100 ,2))]]
        for holding in userHoldings:
            if holding.amount > 0:
                sorting_list.append([])
                sorting_list[-1].append(holding.stock_id.ticket)
                sorting_list[-1].append( float( round(((holding.stock_id.current_price *holding.amount) / player.value ) * 100,2)))
        sorting_list.sort(key = lambda x: x[1])
        for item in sorting_list:
            ticket_list.append(item[0])
            data_list.append(item[1])

        colour_list = CIRCULAR_COLOUR_LIST


        asset_data = {'tickets': ticket_list ,'data' :data_list,'colours': colour_list }
    
    else:
        userFriend = False
        asset_data = 'nothing'   
    errors = []
    return render(request, "trading/other_portfolio.html",{
        'playerName': name,
        'numOfTrades': userTrades,
        'rankRegional': '13',
        'rankOverall': player.portfolio.leaderboard_ranking,
        'totalProfit': f"${(player.value - 50000):,}",
        'totalPortValue': f"${player.value:,}",
        'userFriend': userFriend,
        'lastTraded': lastTrade,
        'portfolio': portfolio,
        'valueData':str({
                "value_history": value_history,
                "dates": dates
            }),
        'assetData':str(asset_data),
        'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
    })