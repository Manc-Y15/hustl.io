from datetime import datetime
from django.utils import timezone
from main.models import Stock



# -------- API modules --------
import finnhub
import json


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

