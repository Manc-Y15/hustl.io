from django.shortcuts import render, redirect
from .models import Stock
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
