from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Subscription

def premium_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this feature.")
            return redirect('login')
        
        try:
            # Check if user has an active subscription
            subscription = Subscription.objects.get(
                user=request.user,
                is_active=True
            )
            
            if subscription:
                # Check if user's profile is premium
                if hasattr(request.user, 'profile') and request.user.profile.is_premium:
                    return function(request, *args, **kwargs)
                else:
                    # Update profile if subscription exists but profile isn't premium
                    request.user.profile.is_premium = True
                    request.user.profile.save()
                    return function(request, *args, **kwargs)
            
        except Subscription.DoesNotExist:
            # No active subscription found
            messages.warning(request, "This feature requires a premium subscription.")
            return redirect('subscribe')
        
        # If we get here, user doesn't have premium access
        messages.warning(request, "This feature requires a premium subscription.")
        return redirect('subscribe')
        
    return wrap

def return_subscription_status(request):
    """
    Return active subscription status for a user without using Stripe
    """
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            is_active=True
        )
        return {
            'has_subscription': True,
            'plan': subscription.plan,
            'created_at': subscription.created_at,
            'is_premium': request.user.profile.is_premium if hasattr(request.user, 'profile') else False
        }
    except Subscription.DoesNotExist:
        return {
            'has_subscription': False,
            'is_premium': False
        }
    
    
    