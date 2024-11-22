from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from checkout.models import Subscription
from django.contrib import messages
from django.contrib.auth.models import User
from profiles.models import Profile
from django.contrib.auth import update_session_auth_hash
import paypalrestsdk
import datetime
from datetime import timedelta  
import time
from django.contrib.auth.forms import PasswordChangeForm
from profiles.forms import EditProfileForm

# Account page for users to see and change PayPal and profile account details
@login_required
def account(request):
    
    """
    Return active subscriptions from a PayPal customer as well as the customer
    and id
    """
    def return_subs():
        customer_id = Subscription.objects.filter(user_id=request.user).first()
        if customer_id:
            customer_id = customer_id.customer_id
            try:
                # Get PayPal billing agreement details
                billing_agreement = paypalrestsdk.BillingAgreement.find(customer_id)
                
                # Check if billing agreement and payer info exists
                if billing_agreement and hasattr(billing_agreement, 'payer') and hasattr(billing_agreement.payer, 'payer_info'):
                    customer = {
                        'email': billing_agreement.payer.payer_info.email
                    }
                else:
                    customer = {}
            
                subscriptions = []
                # PayPal billing agreement represents a single subscription
                if hasattr(billing_agreement, 'plan') and billing_agreement.plan:
                    subscriptions.append({
                        'id': billing_agreement.id,
                        'created': billing_agreement.create_time,
                        'current_period_end': billing_agreement.agreement_details.next_billing_date,
                        'cancel_at_period_end': billing_agreement.state == 'Cancelled',
                        'plan': {
                            'amount': billing_agreement.plan.payment_definitions[0].amount.value
                        }
                    })
                
                # Filter active subscriptions
                active_subscriptions = [sub for sub in subscriptions 
                                      if datetime.datetime.strptime(sub['created'], '%Y-%m-%dT%H:%M:%SZ') < datetime.datetime.now()]
                
            except paypalrestsdk.ResourceNotFound:
                customer = {}
                active_subscriptions = {}
                customer_id = None
            
        else:
            customer = {}
            active_subscriptions = {}
            customer_id = None
        
        return active_subscriptions, customer, customer_id
    
    # If user has submitted change account details form
    if request.method == "POST" and 'account-change-submit' in request.POST:
        password_form = PasswordChangeForm(request.user)
        user_form = EditProfileForm(request.POST, instance=request.user, user=request.user)
        if user_form.is_valid():
            active_subscriptions, customer, customer_id = return_subs()
            user = User.objects.get(pk=request.user.id)
            user_form.save()
            user = User.objects.get(pk=request.user.id)
            # Update email in PayPal if customer exists
            if customer_id:
                # PayPal doesn't support email updates for billing agreements
                # Would need to cancel and create new agreement
                pass
        else:
            # Ensure request.user does not change based on user_form
            user = User.objects.get(pk=request.user.id)
            request.user = user
            active_subscriptions, customer, customer_id = return_subs()
            
    # If user has submitted change password form
    elif request.method == "POST" and 'password-change-submit' in request.POST:
            user_form = EditProfileForm(instance=request.user, user=request.user)
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                active_subscriptions, customer, customer_id = return_subs()
            else:
               active_subscriptions, customer, customer_id = return_subs() 
    else:
        user_form = EditProfileForm(instance=request.user, user=request.user)
        password_form = PasswordChangeForm(request.user)
        active_subscriptions, customer, customer_id = return_subs()
     
        
    context = {
        'password_form': password_form,
        'user_form': user_form,
        'customer': customer,
        'active_subscriptions': active_subscriptions
    }
    
    return render(request, 'account.html', context)
    
# URL to submit cancel subscription request
@login_required   
def cancel_subscription(request, subscription_id):
    
    # Check if subscription belongs to user
    subscription = Subscription.objects.filter(user_id=request.user).first()
    try:
        billing_agreement = paypalrestsdk.BillingAgreement.find(subscription_id)
        if billing_agreement.id != subscription.customer_id:
            messages.error(request, "Authentication failed")
            return redirect(reverse('account'))
        
        # Cancel PayPal billing agreement
        if billing_agreement.cancel({'note': 'Canceling the agreement'}):
            # Update subscription in database
            subscription.is_active = False
            subscription.save()
        else:
            messages.error(request, "Cancellation failed")
            
    except paypalrestsdk.ResourceNotFound:
        messages.error(request, "Subscription not found")
        
    return redirect(reverse('account'))

# URL to request reactivation of subscription
@login_required   
def reactivate_subscription(request, subscription_id):
    
    # PayPal doesn't support reactivating cancelled billing agreements
    # Would need to create a new agreement
    messages.error(request, "Reactivation not supported. Please create a new subscription.")
    return redirect(reverse('account'))
