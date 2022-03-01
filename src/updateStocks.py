from datetime import datetime

from matplotlib.font_manager import json_load
from main.models import Stock
import finnhub
import json
def updateStocks():
    finnhub_client = finnhub.Client(api_key="c875a52ad3i9lkntda8g")
    stocknum = Stock.objects.all().count()
    for stock in Stock.objects.all():
        ## get data
        ticket = stock.ticket
        oldPrice = float(stock.current_price)
        oldDateTime = str(stock.current_datetime)
        newData = finnhub_client.quote(ticket)
        newPrice = newData.get('c')
        newDateTime = datetime.today()
        ## set data
        stock.current_price = newPrice
        stock.current_datetime = newDateTime
        history = json.loads(stock.historical)
        if history.get('history'):
            if len(history['history']) >= 14:
                del history['history'][0]
            history['history'].append({"oldTime": oldDateTime, "oldData": oldPrice})
        else:
            history['history'] = [{"oldTime": oldDateTime, "oldData": oldPrice}]
        stock.historical = json.dumps(history)

        stock.save()
        print('runs to here')

#updateStocks()
