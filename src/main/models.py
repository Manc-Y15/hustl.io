from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Stock(models.Model):
    ticket = models.CharField(max_length=5)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_datetime = models.DateTimeField()
    historical = models.TextField() # Stored as JSON, needs to be large text file
    display_colour = models.TextField(null=True, blank=True)

    day_change = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    week_change = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)


class Holding(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=4)    
    stock_id = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)

class Portfolio(models.Model):
    # below needs to be one to many
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Means user-portfolio is 1-1 and if portfolio is deleted then owner (user) is too.
    # This relationship is the primary key
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bal_hist = models.TextField() # JSON

class League(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="league_owner")
    name = models.CharField(max_length=20)
    starting_balance = models.DecimalField(max_digits=10, decimal_places=2)
    participants = models.ManyToManyField(User, related_name="league_users",default=None, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    icon = models.IntegerField(default=0)


class LeaguePortfolio(models.Model):
    # below needs to be one to many
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    # Means user-portfolio is 1-1 and if portfolio is deleted then owner (user) is too.
    # This relationship is the primary key
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bal_hist = models.TextField() # JSON

class LeagueHolding(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=4)    
    stock_id = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)

@receiver(post_save, sender=League)
def create_league(sender, instance, created, **kwargs):
    if created:
        league_portfolio = LeaguePortfolio()
        league_portfolio.owner = instance.owner
        league_portfolio.league = instance
        league_portfolio.balance = instance.starting_balance
        league_portfolio.bal_hist = '{"history": []}'
        league_portfolio.save()



'''
Slightly confusing part ahead
In order to extend the default Django user model, we
create a OneToOne profile model with each user. 

This allows us to use default django user functions
while also extending the user's attributes
'''
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # requested_friends = models.ManyToManyField(User, related_name='sent_requests',default=None,blank=True)
    requested_me = models.ManyToManyField(User, related_name='received_requests',default=None,blank=True)
    friends = models.ManyToManyField(User, related_name='friends',default=None,blank=True)

# These functions just update the Profile data when User data is updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        user_port = Portfolio()
        user_port.owner = instance
        user_port.balance = 50000
        user_port.bal_hist = '{"history": []}'
        user_port.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    instance.portfolio.save()



class Transaction(models.Model):
    portfolio_id = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stock, on_delete=models.CASCADE)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=4)
    time = models.DateTimeField()
    buy = models.BooleanField(default=True)
    