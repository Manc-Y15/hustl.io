from datetime import datetime
from django.utils import timezone
from main.models import Stock, Portfolio, Holding



# -------- API modules --------
import finnhub
import json


def get_total_value(user_portfolio):
    userHoldings = [holding for holding in Holding.objects.filter(owner = user_portfolio.owner)]
    portfolio_value = user_portfolio.owner.portfolio.balance
    for holding in userHoldings:
        portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
    return portfolio_value

def update_stocks():
    print("[LOG] Updating Stocks")
    successfully_updated = []
    failed = []

    finnhub_client = finnhub.Client(api_key="c875a52ad3i9lkntda8g") # TODO: Make environment variable instead of literal
    stocknum = Stock.objects.all().count()
    for stock in Stock.objects.all():
        # get data
        ticket = stock.ticket
        newData = finnhub_client.quote(ticket)

        # Log success/fails for updates
        if (newData.get('c')): successfully_updated.append(ticket)
        else: failed.append(ticket)
        
        newPrice = newData.get('c')
        newDateTime = timezone.now()
        # set data
        stock.current_price = newPrice
        stock.current_datetime = newDateTime
        history = json.loads(stock.historical)
        if history.get('history'):
            if len(history['history']) >= 14: # Roll over oldest historical value after 14 days.
                del history['history'][0]
            history['history'].append({"oldTime": str(stock.current_datetime), "oldData": float(stock.current_price)})
        else:
            history['history'] = [{"oldTime": str(stock.current_datetime), "oldData": float(stock.current_price)}] # If history doesn't exist for some reason
        stock.historical = json.dumps(history) # Saved as text due to SQLite not supporting JSONField

        if(stock.save()): successfully_updated += 1
    
    success_output = ','.join(successfully_updated)
    failed_output = ','.join(failed)
    print(f"[LOG] {len(successfully_updated)} stocks were updated: {success_output}")
    print(f"[LOG] {len(failed)} stocks failed to update: {failed_output}")

def update_user_portfolio(user_portfolio):
    try:
        history = json.loads(user_portfolio.bal_hist)['history']
    except:
        failed.append(user_portfolio.owner.username)
        return False
    if len(history) >= 7:
        # Cycle next
        del history[0]
        day_date = int(history[5]['oldTime'].split('-')[2].split(' ')[0]) # Split off day number from date
        if int(timezone.now().strftime('%d')) != day_date:
            history.append({"oldTime": str(timezone.now()), "oldData": float(get_total_value(user_portfolio))})
    elif len(history) == 0:
        # fill blanks
        for i in range(0, 7):
            history.append({"oldTime": str(timezone.now()), "oldData": float(get_total_value(user_portfolio))})
    user_portfolio.bal_hist = json.dumps({"history": history})
    user_portfolio.save()

    return True


def update_portfolios():
    # Update value history of all portfolios
    # Would be good to cache this if we were in production but we are not.
    print("[LOG] Updating portfolios")
    successful = []
    failed = []
    for user_portfolio in Portfolio.objects.all():
        if update_user_portfolio(user_portfolio): successful.append(user_portfolio.owner.username)
        else: failed.append(user_portfolio.owner.username)

    success_output = ','.join(successful)
    failed_output = ','.join(failed)
    print(f"[LOG] Successfully updated portfolios for: {success_output}")
    if len(Portfolio.objects.all())-len(successful) > 0:
        print(f"[LOG] Failed to update portfolios for: {failed_output}")

def update_db():
    update_stocks()
    update_portfolios()