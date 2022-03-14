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

class Holding(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=4)    
    stock_id = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)

class Portfolio(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Means user-portfolio is 1-1 and if portfolio is deleted then owner (user) is too.
    # This relationship is the primary key
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bal_hist = models.TextField() # JSON

'''
Slightly confusing part ahead
In order to extend the default Django user model, we
create a OneToOne profile model with each user. 

This allows us to use default django user functions
while also extending the user's attributes
'''
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requested_friends = models.ManyToManyField(User, related_name='received_requests',default=None,blank=True)
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
    