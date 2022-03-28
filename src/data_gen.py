from main.models import Stock, Holding, Portfolio, Transaction, User
from main.transactions import user_buy, user_sell_all
from stock_updater import update_user_portfolio
import random


f = open("names.txt", "r")
names = f.read().split('\n')

endings = [
    "TheHustler",
    "_FTW",
    "_WSTREET",
    "2MOON",
    "_hustler"
]


def gen_data(amount):
    for i in range(amount):
        gen_username = create_username()
        user = User.objects.create_user(username=gen_username, email=gen_username + '@fakeuser.com', password='fakeassuser')  
        user.save()


        for j in range(random.randint(1, 6)):
            random_stock = random.choice(Stock.objects.all())
            user_buy(user, is_buy=True, stock_id=random_stock.ticket, amount=random.randint(0, 6000))

        user.portfolio.balance += random.randint(-5000, 5000)
        user.portfolio.save()

        print(user.username)
        
    

def create_username():
    name = random.choice(names)

    if random.randint(0, 10) >= 5:
        name += "_" + random.choice(names)
    
    if random.randint(0, 10) >= 8:
        name += random.choice(endings)
    
    if random.randint(0, 10) >= 6:
        name += str(random.randint(0, 9999))
    return name


def get_stocks():
    stocks = []

    for db_stock in Stock.objects.all():
        stock = {}
        stock['ticket'] = db_stock.ticket
        stock['name'] = db_stock.name
        stock['description'] = db_stock.desc
        stock['current_price'] = db_stock.current_price
        stock['historical'] = db_stock.historical
        stock['display_colour'] = db_stock.display_colour
        stocks.append(stock)
    return stocks
    
