# Generated by Django 3.1.7 on 2021-03-29 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_order_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='amount',
            field=models.FloatField(default='1'),
            preserve_default=False,
        ),
    ]
