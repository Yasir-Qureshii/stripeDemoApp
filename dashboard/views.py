from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django_registration.backends.one_step.views import RegistrationView
from django import forms
import stripe
import json

from .models import Subscription
stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
@login_required(login_url='login')
def home(request):
    # customer = stripe.Customer.create(
    #     name=request.user.username
    # )
    #
    # subscription = stripe.Subscription.create(
    #     customer=customer.id,
    #     items=[
    #         {"price": settings.STRIPE_PRICE_ID}
    #     ],
    # )
    #
    # Subscription.objects.create(
    #     user=request.user,
    #     stripeCustomerId=customer.id,
    #     stripeSubscriptionId=subscription.id
    # )
    subscription = Subscription.objects.get(user=request.user)
    context = {
        'subscription': subscription
    }
    if subscription.stripePaymentId:
        payment_obj = stripe.PaymentMethod.retrieve(
            subscription.stripePaymentId,
        )
        context['payment_obj'] = payment_obj
    return render(request, 'accounts/dashboard.html', context)


# @login_required(login_url='login')
def add_payment(request):
    context = {}
    user = request.user
    subscription = Subscription.objects.get(user=user)
    # if request.method == 'POST':
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        card_no = request.POST.get('card_no')
        expiry = request.POST.get('expiry')
        exp_month, exp_year = expiry.split('/')
        cvc = request.POST.get('cvc')

        try:
            # Create payment method
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": card_no,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
                },
            )

            # attach payment method to customer
            payment_method = stripe.PaymentMethod.attach(
                payment_method.id,
                customer=subscription.stripeCustomerId
            )

            # make this the default payment method
            stripe.Customer.modify(
                subscription.stripeCustomerId,
                invoice_settings={
                    "default_payment_method": payment_method.id,
                },
            )

            # attach this payment method to subscription object
            # subscription.stripePaymentId = payment_method.id
            # subscription.save()
            return HttpResponse("Payment Method Added Successfully!")
            # return redirect('/')

            # # create customer subscription on stripe
            # subscription = stripe.Subscription.create(
            #     customer=subscription.stripeCustomerId,
            #     items=[
            #         {"price": settings.STRIPE_PRICE_ID}
            #     ]
            # )
            #
            # # create subscription object in db
            # Subscription.objects.create(
            #     user=user,
            #     stripeCustomerId=customer.id,
            #     stripeSubscriptionId=subscription.id
            # )

        except stripe.error.CardError as e:
            print("stripe_message", e.user_message)
            response = HttpResponse(e.user_message)
            response.status_code = 400
            return response
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def first_login(request):
    user = request.user
    subscription = Subscription.objects.get(user=request.user)
    context = {
        'subscription': subscription
    }
    try:
        # Create customer on stripe
        customer = stripe.Customer.create(
            email=user.email,
            name=user.username
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
            user=user,
            stripeCustomerId=customer.id,
            stripeSubscriptionId=subscription.id
        )

    except stripe.error.CardError as e:
        print("stripe_http_status", e.http_status)
        print("stripe_error_code", e.code)
        print("stripe_message", e.user_message)
        if int(e.http_status) != 200:
            context['payment_added'] = True
            context['stripe_message'] = e.user_message

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def cancel_subscription(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
        stripe.Subscription.delete(
            subscription.stripeSubscriptionId
        )
        subscription.state = 'canceled'
        subscription.save()
    except stripe.error.CardError as e:
        print("stripe_http_status", e.http_status)
        print("stripe_error_code", e.code)
        print("stripe_message", e.user_message)

    subscription = Subscription.objects.get(user=request.user)
    context = {
        'subscription': subscription
    }
    return render(request, 'accounts/dashboard.html', context)


class customSignup(RegistrationView):
    subscribed = forms.CharField(max_length=100)

    def register(self, form):
        subscribed = form.data.get('subscribed')
        if subscribed == 'on':
            print('user subscribed')
        else:
            print('user not subscribed')
            error = "You must subscribe for Aben Premium membership"
            form.errors['subscription'] = error
            return False
        if form.is_valid():
            pass




