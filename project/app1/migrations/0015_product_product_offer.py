# Generated by Django 4.2.1 on 2023-06-16 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_customer_referral_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_offer',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
