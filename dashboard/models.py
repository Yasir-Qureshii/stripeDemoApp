from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Subscription(models.Model):
    subscriptions = (
        ('trialing', 'trialing'),
        ('active', 'active'),
        ('canceled', 'canceled'),
        ('unpaid', 'unpaid'),
        ('incomplete', 'incomplete'),
        ('incomplete_expired', 'incomplete_expired'),
    )
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    state = models.CharField(max_length=200, choices=subscriptions, default=subscriptions[0][0])
    stripeCustomerId = models.CharField(max_length=900)
    stripeSubscriptionId = models.CharField(max_length=900)
    stripePaymentId = models.CharField(max_length=900, null=True)

    def __str__(self):
        return self.user.username
