from .models import Stock, Portfolio, Holding, Profile, Transaction, League, LeaguePortfolio

def create_league(owner, name, starting_balance, icon):
    if name in [league.name for league in League.objects.all()]:
        return (False, "Name already in use")
    new_league = League()
    new_league.owner = owner
    new_league.name = name
    new_league.starting_balance = starting_balance
    new_league.icon = icon
    new_league.save()
    return (True, "Successfully created league.")

def add_user(league, user):
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
  

def remove_user(league, user):
    if user not in league.participants.all():
        return (False, "User not in league.")
    
    league.participants.remove(user)
    league.save()
    user_port = League.objects.filter(owner = user)[0]
    user_port.delete()
    user_port.save()

    return (True, f"Successfully removed {user.username}")