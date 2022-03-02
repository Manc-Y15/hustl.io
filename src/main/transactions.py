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












# get holdings by user, get total value of all holdings, get distribution for holdings

# return all holdings associated with user
def get_holdings(user):
    return Holding.objects.filter(owner=user)

# Total value of holdings, DOES NOT INCLUDE raw cash
def holdings_total(user):
    total = 0
    for holding in get_holdings(user):
        stock = holding.stock_id

        total += stock.current_price * holding.amount
    return total


# Returns dict of each holding name (key) and the value in cash for it, including raw cash held
def holdings_distribution(user):
    distribution = {"cash": user.portfolio.balance}
    for holding in get_holdings(user):
        stock = holding.stock_id

        value = stock.current_price * holding.amount # get value of this holding

        distribution[stock.ticket] = value
    
    return distribution
