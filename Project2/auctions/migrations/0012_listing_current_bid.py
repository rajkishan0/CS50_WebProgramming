# Generated by Django 2.2.11 on 2020-07-17 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auto_20200717_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]