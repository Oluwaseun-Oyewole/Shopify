# Generated by Django 3.1.7 on 2021-04-09 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_item_item_choice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_choice',
            field=models.CharField(blank=True, choices=[('N', 'NEW'), ('B', 'BESTSELLER'), ('', '')], max_length=1, null=True),
        ),
    ]
