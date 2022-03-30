from .models import Stock, Portfolio, Holding, Profile, Transaction, League, LeaguePortfolio, LeagueHolding, User
from random import randint
from .constants import *

def create_league(owner, name, starting_balance, icon):
    if name in [league.name for league in League.objects.all()]:
        return (False, "Name already in use")
    if float(starting_balance) <= 1000 :
        return (False, "Starting balance must be greater than $1000")
    new_league = League()
    new_league.owner = owner
    new_league.name = name
    new_league.starting_balance = starting_balance
    new_league.icon = randint(0, len(ICON_LIST)-1)
    new_league.save()
    return (True, "Successfully created league.")

def add_member_backend(league, memberName):
    if not User.objects.filter(username = memberName).exists():
        return (False, "User does not  exist.")    

    user = User.objects.filter(username = memberName)[0]
    
    if user not in league.owner.profile.friends.all():
        return(False, "You are not friends with this User")       
    if user in league.participants.all():
        return (False, "User already in league.")
    league.participants.add(user)
    league.save()    
    league_portfolio = LeaguePortfolio()
    league_portfolio.owner = user
    league_portfolio.league = league
    league_portfolio.balance = league.starting_balance
    league_portfolio.bal_hist = '{"history": []}'
    league_portfolio.save()

    return (True, f"Successfully added {user.username}")
    

def remove_member_backend(league, user):
    if user not in league.participants.all():
        return (False, "User not in league.")
    holdings = [holding for holding in LeagueHolding.objects.filter(owner = user, league = league)]
    
    for holding in holdings:
        holding.delete()
        holding.save()
    league.participants.remove(user)
    league.save()
    user_port = LeaguePortfolio.objects.filter(league=league, owner = user)[0]
    user_port.delete()
    user_port.save()

    return (True, f"Successfully removed {user.username}")