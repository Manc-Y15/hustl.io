from datetime import datetime
from matplotlib.font_manager import json_load
from main.models import Stock

# -------- API modules --------
import finnhub
import json


def update_stocks():
    finnhub_client = finnhub.Client(api_key="c875a52ad3i9lkntda8g") # TODO: Make environment variable instead of literal
    stocknum = Stock.objects.all().count()
    for stock in Stock.objects.all():
        # get data
        ticket = stock.ticket
        oldPrice = float(stock.current_price) # Decimal --> Float
        oldDateTime = str(stock.current_datetime) # Datetimes not supported in JSON lib, converted to string
        newData = finnhub_client.quote(ticket)
        newPrice = newData.get('c')
        newDateTime = datetime.today()
        # set data
        stock.current_price = newPrice
        stock.current_datetime = newDateTime
        history = json.loads(stock.historical)
        if history.get('history'):
            if len(history['history']) >= 14: # Roll over oldest historical value after 14 days.
                del history['history'][0]
            history['history'].append({"oldTime": oldDateTime, "oldData": oldPrice})
        else:
            history['history'] = [{"oldTime": oldDateTime, "oldData": oldPrice}] # If history doesn't exist for some reason
        stock.historical = json.dumps(history) # Saved as text due to SQLite not supporting JSONField

        stock.save()


