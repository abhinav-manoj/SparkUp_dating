from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Order(models.Model):
    PLANS = (
        ('plan_F5eyGdYCvZPtON', 'Monthly - £24.99'),
        ('plan_F5ey2nnZwy5v8Q', '3 Months - £44.99'),
        ('plan_F5eyNlWXHig7YB', '6 Months - £74.99'),
        )
    plans = models.CharField(choices=PLANS, default='plan_F5ey2nnZwy5v8Q', blank=False, max_length=100)
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    country = models.CharField(max_length=40, blank=False)
    postcode = models.CharField(max_length=20, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    street_address1 = models.CharField(max_length=40, blank=False)
    street_address2 = models.CharField(max_length=40, blank=False)
    county = models.CharField(max_length=40, blank=False)
    date = models.DateField()
    
    def __str__(self):
        return "{0}-{1}-{2}".format(self.id, self.date, self.full_name)

    class Meta:
        db_table = 'checkout_order'

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    customer_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'checkout_subscription'

    def __str__(self):
        return f"{self.user.username}'s {self.plan} subscription"