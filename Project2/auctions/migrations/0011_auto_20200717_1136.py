# Generated by Django 2.2.11 on 2020-07-17 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(default='Other', max_length=10),
        ),
    ]
