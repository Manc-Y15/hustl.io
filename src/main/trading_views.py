from django.shortcuts import render, redirect
from .models import Stock,Holding,Portfolio,Transaction
from .transactions import user_buy
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

def asset_page(request, ticket):
    if request.method == "POST":
        transaction = {
            "is_buy": True if (request.POST.get("transaction", "") == "buy") else False,
            "stock_id": ticket, 
            "amount": request.POST.get("amount", "")
        }
        if user_buy(request.user, transaction['is_buy'], transaction['stock_id'], float(transaction['amount'])):
            print("SUCCESS")
        else: print("FAIL")


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
        return render(request, 'trading/stock_listing.html', {
            'stock': stock,
            'data': str({
                "value_history": value_history,
                "dates": dates
            })
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
    userProfit = f"${(portfolio.balance  - 50000):,}"

    # Last trade query & colour setting
    lastTrade = Transaction.objects.filter(portfolio_id = portID).last().stock_id
    cols = lastTrade.display_colour.split(' ')
    lastTrade.col1 = cols[0].split('(')[1][:-1]
    lastTrade.col2 = cols[1].split('(')[1][:-1]

    # getting data for the line graph
    historical_balance = json.loads(portfolio.bal_hist)['history']
    if historical_balance[8]['oldData'] > historical_balance[len(historical_balance)-1]['oldData']:
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