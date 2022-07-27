from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name="home"),
    path('add-payment', views.add_payment, name="add_payment"),
    path('subscribe', views.first_login, name="subscribe"),
    path('cancel_subscription', views.cancel_subscription, name="cancel_subscription"),
    # path('signup', views.customSignup.as_view(), name="custom_signup"),
]
