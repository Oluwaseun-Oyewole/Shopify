# Generated by Django 3.1.7 on 2021-03-29 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20210327_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
