# Generated by Django 3.1.7 on 2021-03-30 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='email',
            field=models.EmailField(default='findseun@gmail.com', max_length=254),
            preserve_default=False,
        ),
    ]
