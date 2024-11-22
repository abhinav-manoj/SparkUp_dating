import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import OrderForm, MakePaymentForm
from .models import Subscription
from profiles.models import Profile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

# Configure PayPal SDK
paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_SECRET_KEY
})

# Function to update user profile to premium
def make_user_premium(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.is_premium = True
    profile.save()

# Subscribe page, allowing users to create a PayPal subscription
@login_required
def subscribe(request):
    plan_ids = {
        'plan_F5eyNlWXHig7YB': '6 Monthly',
        'plan_F5ey2nnZwy5v8Q': '3 Monthly',
        'plan_F5eyGdYCvZPtON': 'Monthly'
    }
    
    # If user submits payment form
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)
        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            order.save()

            subscription = Subscription.objects.filter(user_id=request.user.id).first()
            
            # If user has subscribed before and has customer record
            if subscription:
                # Create a PayPal payment
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "transactions": [{
                        "amount": {
                            "total": str(order.price),  # Replace with price from order
                            "currency": "GBP"  # Or the relevant currency
                        },
                        "description": f"Subscription for {order.plan}"
                    }],
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(reverse('payment_success')),
                        "cancel_url": request.build_absolute_uri(reverse('payment_cancel'))
                    }
                })

                if payment.create():
                    for link in payment.links:
                        if link.rel == "approval_url":
                            approval_url = link.href
                            return redirect(approval_url)  # Redirect to PayPal for payment

                else:
                    messages.error(request, "Error with PayPal payment creation.")
                    return redirect(reverse('subscribe'))
            
            else:
                # New subscription
                subscription = Subscription(
                    user=request.user, 
                    plan=plan_ids[order.plans], 
                    customer_id=payment.id
                )
                subscription.save()
                make_user_premium(request)
                messages.success(request, "Success! You are now a premium user")
                return redirect(reverse('index'))
        else:
            messages.error(request, "Unable to take payment")
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()
      
    return render(request, 'subscribe.html', {'page_ref': 'subscribe', 'order_form': order_form, 'payment_form': payment_form})
from django.shortcuts import render, redirect
from django.contrib import messages
import paypalrestsdk

# Handle payment success
@login_required
def payment_success(request):
    # Get the user's profile
    profile = Profile.objects.get(user_id=request.user.id)
    
    # Make user premium
    profile.is_premium = True
    profile.save()
    
    # Create or update subscription record
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={
            'plan': request.session.get('selected_plan', 'Monthly'),
            'customer_id': f"pp_{timezone.now().timestamp()}",  # Generate a unique ID
            'is_active': True
        }
    )
    
    if not created:
        subscription.plan = request.session.get('selected_plan', 'Monthly')
        subscription.is_active = True
        subscription.save()
    
    messages.success(request, "Payment successful! You are now a premium member!")
    return render(request, 'checkout/payment_success.html')
# Handle payment cancellation
def payment_cancel(request):
    messages.error(request, "Payment was cancelled. Please try again.")
    return redirect('subscribe')

@require_POST
def store_plan(request):
    data = json.loads(request.body)
    plan = data.get('plan')
    request.session['selected_plan'] = plan
    return JsonResponse({'status': 'success'})
