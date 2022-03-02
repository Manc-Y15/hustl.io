from  datetime import datetime
from django.utils import timezone
from .models import Holding, Stock, Portfolio,Transaction

from decimal import Decimal

# handle buy transaction
# take in amount, is buy
# user balance = balance - (amount * price for that stock)
# add to transaction table portfolio,stock,price,amount,datetime,isbuy

def user_buy(user, is_buy, stock_id, amount):
    if amount != 0:
        stock = Stock.objects.filter(ticket = stock_id)[0]
        volume = amount / float(stock.current_price)
        if is_buy:
            purchase = 'BUY'
            if amount > user.portfolio.balance:
                return False
        else:
            if volume > Holding.objects.filter(owner = user, stock_id = stock)[0]:
                return False
            purchase = 'SELL'
            amount = amount * -1 # makes the amount negative. The amount is subtracted from the balance.
        user.portfolio.balance -= Decimal.from_float(float(amount))
        
        timeOfBuy = timezone.now()
        transac = Transaction()
        transac.portfolio_id = (user.portfolio)
        transac.stock_id = stock
        transac.buy_price = stock.current_price
        transac.volume = Decimal.from_float(volume)
        transac.time = timeOfBuy
        transac.buy = is_buy
        user.portfolio.save()
        transac.save()
        return True
    else:
        return False