from django.shortcuts import render, redirect
from .models import Stock
from random import randint
import json
from datetime import datetime
import calendar



def asset_page(request, ticket):
    query_matches = Stock.objects.filter(ticket=ticket)
    if len(query_matches) != 1:
        return render(request, 'home.html', {})
    else:
        stock = query_matches[0]
        historical_prices = json.loads(stock.historical)['history']
        raw_day_dates = [datum['oldTime'].split(' ')[0] for datum in historical_prices]
        dates = []
        for raw in raw_day_dates:
            split = raw.split('-')
            dates.append(calendar.month_name[int(split[1])][:3].upper() + " " + split[2])
        return render(request, 'trading/stock_listing.html', {
            'stock': {
                'ticket': stock.ticket,
                'name': stock.name,
                'desc': stock.desc,
                'curr_price': stock.current_price,
            },
            'data': str({
                "value_history": [f"{datum['oldData']:.2f}" for datum in historical_prices],
                "dates": dates
            })
        }
        )

