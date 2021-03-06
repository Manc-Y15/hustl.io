from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Stock,Profile,Portfolio,Holding,User,League
from .constants import *
    
def getPortfolioValue(player):   
    userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
    player.portfolio_value = player.portfolio.balance
    for holding in userHoldings:
        player.portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
    return(player.portfolio_value)

#Function to calculate percentage price between previous and currrent price
def percentage_change(prev_price, current_price):
    change_in_price = current_price-prev_price
    percentage_change = round((change_in_price/prev_price)*100,2)
    return (percentage_change)
    # print(percentage_change),"%"

#Function to calculate average price over list of of prices
def average_price(price_list):
    sum = 0
    for i in price_list:
        sum += i
    average = round(sum/len(price_list))
    # print(average)

#Highest and Lowest prices
def high_and_low(price_list):
    highest_price = max(price_list)
    lowest_price = min(price_list)
    #print("Lowest price is: " + str(lowest_price) + "\nHighest price is: " + str(highest_price))

def get_user_leagues(user):
    if not user.is_authenticated: return []
    to_return = []
    for league in League.objects.filter(owner=user):
        league.league_icon = ICON_LIST[league.icon]
        to_return.append(league)
    for league in League.objects.all():
        if user in league.participants.all(): 
            league.league_icon = ICON_LIST[league.icon]
            to_return.append(league)
    return to_return
    
    


   