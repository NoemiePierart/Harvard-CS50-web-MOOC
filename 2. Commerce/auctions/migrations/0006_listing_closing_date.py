# Generated by Django 3.1.2 on 2020-10-21 19:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20201021_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='closing_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
