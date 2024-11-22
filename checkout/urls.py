from django.urls import path
from .views import subscribe, payment_success, payment_cancel, store_plan

urlpatterns = [
    path('', subscribe, name='subscribe'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
    path('store-plan/', store_plan, name='store_plan'),
]