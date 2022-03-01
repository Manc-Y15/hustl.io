from django.shortcuts import render, redirect
from .models import Stock
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
    query_matches = Stock.objects.filter(ticket=ticket)
    if len(query_matches) != 1:
        return render(request, 'home.html', {})
    else:
        stock = query_matches[0]
        historical_prices = json.loads(stock.historical)['history']
        if historical_prices[0]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            stock.pos = True
        else: stock.pos = False

        cols = stock.display_colour.split(' ')
        stock.col1 = cols[0].split('(')[1][:-1]
        stock.col2 = cols[1].split('(')[1][:-1]

        raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_prices]
        dates = []
        for raw in raw_day_dates:
            split = raw.split('-')
            dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        return render(request, 'trading/stock_listing.html', {
            'stock': stock,
            'data': str({
                "value_history": [f"{datum['oldData']:.2f}" for datum in historical_prices],
                "dates": dates
            })
        }
        )

def asset_list_page(request):
    stocks = [stock for stock in Stock.objects.all()]
    positive = {}
    for stock in stocks:
        historical_prices = json.loads(stock.historical)['history']
        if historical_prices[0]['oldData'] > historical_prices[len(historical_prices)-1]['oldData']:
            stock.pos = True
        else: stock.pos = False

        cols = stock.display_colour.split(' ')
        stock.col1 = cols[0]
        stock.col2 = cols[1]
        #stock.background = choose_background(stock)
    return render(request, "trading/stock_list.html", {
        'stocks': stocks
    })
