from  datetime import datetime
from django.utils import timezone
from .models import Holding, LeaguePortfolio, Stock, Portfolio,Transaction, LeagueHolding, League

from decimal import Decimal

# handle buy transaction
# take in amount, is buy
# user balance = balance - (amount * price for that stock)
# add to transaction table portfolio,stock,price,amount,datetime,isbuy

def user_sell_all(user,stock_id, league="global"):
    if league=="global":
        stock = Stock.objects.filter(ticket = stock_id)[0]
        if (Holding.objects.filter(owner = user, stock_id = stock).exists() 
        and  Holding.objects.filter(owner = user, stock_id = stock)[0].amount > 0 ):
            holding =  Holding.objects.filter(owner = user, stock_id = stock)[0]
            user.portfolio.balance += holding.amount * stock.current_price
            amount_sold = holding.amount * stock.current_price
            tempAmount =  holding.amount
            holding.amount = 0.0
            holding.save()
            timeOfBuy = timezone.now()
            transac = Transaction()
            transac.portfolio_id = (user.portfolio)
            transac.stock_id = stock
            transac.buy_price = stock.current_price
            transac.volume = tempAmount
            transac.time = timeOfBuy
            transac.buy = False
            user.portfolio.save()
            transac.save()        
            return(True, f"Successfully sold ${amount_sold}")
        else:
            return(False,"You don't own any of this stock")
    else:
        stock = Stock.objects.filter(ticket = stock_id)[0]
        if (LeagueHolding.objects.filter(owner = user, stock_id = stock).exists() 
        and LeagueHolding.objects.filter(owner = user, stock_id = stock)[0].amount > 0 ):
            leagueobj = League.objects.filter(name = league)[0]
            holding =  LeagueHolding.objects.filter(owner = user, stock_id = stock, league=leagueobj)[0]
            portfolio = LeaguePortfolio.objects.filter(league=leagueobj)[0]
            portfolio.balance += holding.amount * stock.current_price
            amount_sold = holding.amount * stock.current_price
            tempAmount =  holding.amount
            holding.amount = 0.0
            holding.save()            
            portfolio.save()
            return(True, f"Successfully sold ${amount_sold}")
        else:
            return(False,"You don't own any of this stock")
        
def user_buy(user, is_buy, stock_id, amount, league="global"):
    # check to see if user has bought the stock before
    stock = Stock.objects.filter(ticket = stock_id)[0]
    
    if league == "global":
        if Holding.objects.filter(owner = user, stock_id = stock).exists():
            firstBuy = False
        else:
            firstBuy = True
        if amount != 0:
            if amount > (stock.current_price/100):
                volume = amount / float(stock.current_price)
                if is_buy:
                    purchase = 'BUY'
                    if amount > user.portfolio.balance:
                        return (False, "You don't have enough money to buy this amount.")
                else:
                    if volume > Holding.objects.filter(owner = user, stock_id = stock)[0].amount:
                        return (False, "You don't own enough of this asset to sell this amount.")
                    purchase = 'SELL'
                    amount = amount * -1 # makes the amount negative. The amount is subtracted from the balance.
                    volumeSell = volume * -1
                user.portfolio.balance -= Decimal.from_float(float(amount))
                if firstBuy == False:
                    thisHolding = Holding.objects.filter(owner = user, stock_id = stock)[0]
                    if is_buy:
                        x = float(thisHolding.amount) + volume
                        thisHolding.amount = Decimal.from_float(x)
                        thisHolding.save()
                    else:
                        x = float(thisHolding.amount) - volume
                        thisHolding.amount = Decimal.from_float(x)
                        thisHolding.save()
                else:
                    newHolding = Holding()
                    newHolding.owner = user
                    newHolding.amount = volume
                    newHolding.stock_id = stock
                    newHolding.save()
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
                return (True, "")
            else:
                return (False, f"Minimum purchase ${round(float(stock.current_price) * 0.01,2)} (1%) of the stock price")
        else:
            return (False, "No amount specified.")
    else:
        if LeagueHolding.objects.filter(owner = user, stock_id = stock).exists():
            firstBuy = False
        else:
            firstBuy = True
        if amount != 0:
            leagueobj = League.objects.filter(name = league)[0]
            league_portfolio = LeaguePortfolio.objects.filter(owner = user, league = leagueobj)[0]
            if amount > (stock.current_price/100):
                volume = amount / float(stock.current_price)
                if is_buy:
                    purchase = 'BUY'
                    if amount > league_portfolio.balance:
                        return (False, "You don't have enough money to buy this amount.")
                else:
                    if volume > LeagueHolding.objects.filter(owner = user, stock_id = stock)[0].amount:
                        return (False, "You don't own enough of this asset to sell this amount.")
                    purchase = 'SELL'
                    amount = amount * -1 # makes the amount negative. The amount is subtracted from the balance.
                    volumeSell = volume * -1
                league_portfolio.balance -= Decimal.from_float(float(amount))
                if firstBuy == False:
                    thisHolding = LeagueHolding.objects.filter(owner = user, stock_id = stock)[0]
                    if is_buy:
                        x = float(thisHolding.amount) + volume
                        thisHolding.amount = Decimal.from_float(x)
                        thisHolding.save()
                    else:
                        x = float(thisHolding.amount) - volume
                        thisHolding.amount = Decimal.from_float(x)
                        thisHolding.save()
                else:
                    newHolding = LeagueHolding()
                    newHolding.owner = user
                    newHolding.amount = volume
                    newHolding.stock_id = stock
                    newHolding.league = leagueobj
                    newHolding.save()
                league_portfolio.save()
                return (True, "")
            else:
                return (False, f"Minimum purchase ${round(float(stock.current_price) * 0.01,2)} (1%) of the stock price")
        else:
            return (False, "No amount specified.")