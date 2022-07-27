from datetime import datetime
from django.shortcuts import get_object_or_404
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.conf import settings
import stripe
from .models import Subscription
stripe.api_key = settings.STRIPE_SECRET_KEY


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create customer on stripe
        customer = stripe.Customer.create(
            email=instance.email,
            name=instance.username
        )

        # create customer subscription on stripe
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {"price": settings.STRIPE_PRICE_ID}
            ],
            trial_period_days=7
        )

        # create subscription object in db
        Subscription.objects.create(
            user=instance,
            stripeCustomerId=customer.id,
            stripeSubscriptionId=subscription.id
        )
