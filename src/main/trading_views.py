from django.shortcuts import render, redirect, HttpResponse
from .models import Stock, Holding, Portfolio, Transaction
from django.contrib.auth.decorators import login_required
from .transactions import user_buy, user_sell_all
from random import randint, choice
import json
from datetime import datetime
import calendar


backgrounds = [
    "var(--emerald) var(--turquoise)",
    "var(--turquoise) var(--amethyst)",
    "var(--sun-flower) var(--carrot)",
    "var(--wisteria) var(--pumpkin)",
    "var(--clouds) var(--river) ",
]


def choose_background(stock):
    if stock.current_price < 100:
        return backgrounds[0]
    elif stock.current_price < 500:
        return backgrounds[1]
    elif stock.current_price < 1000:
        return backgrounds[2]
    elif stock.current_price < 2000:
        return backgrounds[3]
    elif stock.current_price < 3000:
        return backgrounds[4]

def asset_page_form(request):
    if request.method == "POST":
        form = {}
        transaction = {}
        if request.POST.get("transaction", "") == "sellall":
            stock = Stock.objects.filter(ticket =  request.POST.get("ticket", ""))[0]
            if Holding.objects.filter(owner = request.user, stock_id = stock).exists():
                holding =  Holding.objects.filter(owner =  request.user, stock_id = stock)[0]
                transaction['amount'] = holding.amount * stock.current_price

                order = user_sell_all(request.user, request.POST.get("ticket", ""))

                if order[0]:
                    form['success'] = True
                else:
                    transaction['error'] = order[1]
                    form['success'] = False
                transaction['is_buy'] = False
                transaction['stock_id'] = request.POST.get("ticket", "")
            else:
                form['success'] = False
            
        else:
            transaction = {
                "is_buy": True if (request.POST.get("transaction", "") == "buy") else False,
                "stock_id": request.POST.get("ticket", ""), 
                "amount": request.POST.get("amount", "")
            }
            order = user_buy(request.user, transaction['is_buy'], transaction['stock_id'], float(transaction['amount']))
            if order[0]:
                form['success'] = True
            else:
                transaction['error'] = order[1]
                form['success'] = False
        stock = Stock.objects.filter(ticket=request.POST.get("ticket", ""))[0]
        cols = stock.display_colour.split(' ')
        stock.col1 = cols[0].split('(')[1][:-1]
        stock.col2 = cols[1].split('(')[1][:-1]

        return render(request, 'trading/stock_listing_response.html', {"form": form, "transaction": transaction, "stock": stock})
        

def asset_page(request, ticket):
    print('here')
    query_matches = Stock.objects.filter(ticket=ticket)
    if len(query_matches) != 1:
        return render(request, 'home.html', {})
    else:
        stock = query_matches[0]
        historical_prices = json.loads(stock.historical)['history']
        if historical_prices[8]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            stock.pos = False
        else: stock.pos = True

        cols = stock.display_colour.split(' ')
        stock.col1 = cols[0].split('(')[1][:-1]
        stock.col2 = cols[1].split('(')[1][:-1]

        raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_prices]
        dates = []
        for raw in raw_day_dates:
            split = raw.split('-')
            dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        
        value_history = [f"{datum['oldData']:.2f}" for datum in historical_prices]
        if len(dates) > 7: 
            value_history = value_history[7:]
            dates = dates[7:]
    if request.user.is_authenticated:
        transactions = []
        activity = ''
        
        # activity feed
        activity = "Activity Feed"
        thisStock = Stock.objects.filter(ticket=ticket)[0]
        allTransactions = Transaction.objects.filter(stock_id = thisStock)
        activityFeed = []
        transactions = []
        for transac in allTransactions:
            if transac.portfolio_id.owner == request.user:
                activityFeed.append(transac)
            elif transac.portfolio_id.owner in request.user.profile.friends.all():
                activityFeed.append(transac)
            else:
                pass
        for transac in activityFeed:
            transactions.append([])
            newtransacaction = transactions[-1]
            newtransacaction.append(transac.portfolio_id.owner.username)
            if transac.buy == True:
                newtransacaction.append('bought')
            else:
                newtransacaction.append('sold')
            newtransacaction.append(round(transac.buy_price * transac.volume,2))
            newtransacaction.append(transac.stock_id.ticket)
            newtransacaction.append(transac.stock_id.current_price)
            newtransacaction.append(transac.time)
        transactions.reverse()
        transactions = transactions[:6]
    else:
        transactions = []
        activity = ''

    
    return render(request, 'trading/stock_listing.html', {
        'stock': stock,
        'transactions': transactions,
        'activity': activity,
        'data': str({
            "value_history": value_history,
            "dates": dates
        }),
    }
    )

def asset_list_page(request):
    stocks = [stock for stock in Stock.objects.all()]
    positive = {}
    for stock in stocks:
        historical_prices = json.loads(stock.historical)['history']
        if historical_prices[7]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            stock.pos = False
        else: stock.pos = True

        cols = stock.display_colour.split(' ')
        stock.col1 = cols[0]
        stock.col2 = cols[1]
        #stock.background = choose_background(stock)
    return render(request, "trading/stock_list.html", {
        'stocks': stocks
    })

@login_required
def portfolio_view(request):
    userHoldings = [holding for holding in Holding.objects.filter(owner = request.user)]
    for holding in userHoldings:
        cols = holding.stock_id.display_colour.split(' ')
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

    portfolio.display_colour = "var(--turquoise) var(--amethyst)"
    cols = portfolio.display_colour.split(' ')
    portfolio.col1 = cols[0].split('(')[1][:-1]
    portfolio.col2 = cols[1].split('(')[1][:-1]

    raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_balance]
    dates = []
    for raw in raw_day_dates:
        split = raw.split('-')
        dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        
    value_history = [f"{datum['oldData']:.2f}" for datum in historical_balance]
    if len(dates) > 7: 
        value_history = value_history[7:]
        dates = dates[7:]
    # asset graph
    ticket_list = []
    data_list = []
    sorting_list = [['Cash',float(round((portfolio.balance / totalPortValue ) * 100 ,2))]]
    for holding in userHoldings:
        if holding.amount > 0:
            sorting_list.append([])
            sorting_list[-1].append(holding.stock_id.ticket)
            sorting_list[-1].append( float( round((holding.stock_id.balance / totalPortValue ) * 100,2)))
    sorting_list.sort(key = lambda x: x[1])
    for item in sorting_list:
        ticket_list.append(item[0])
        data_list.append(item[1])

    colour_list = [
    "--river", 
    "--emerald", 
    "--turquoise", 
    "--amethyst",
    "--green-sea",
    "--nephritis",
    "--wisteria",
    "--sun-flower",
    "--carrot",
    "--alizarin",
    "--orange"
    ]

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