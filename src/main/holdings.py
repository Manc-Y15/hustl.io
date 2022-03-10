from .models import Holding, Stock
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
