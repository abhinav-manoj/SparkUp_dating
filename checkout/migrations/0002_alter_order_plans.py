# Generated by Django 5.0.7 on 2024-11-21 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='plans',
            field=models.CharField(choices=[('plan_F5eyGdYCvZPtON', 'Monthly - £24.99'), ('plan_F5ey2nnZwy5v8Q', '3 Months - £44.99'), ('plan_F5eyNlWXHig7YB', '6 Months - £74.99')], default='plan_F5ey2nnZwy5v8Q', max_length=100),
        ),
    ]