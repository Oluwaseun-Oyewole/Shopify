# Generated by Django 3.1.7 on 2021-03-22 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
