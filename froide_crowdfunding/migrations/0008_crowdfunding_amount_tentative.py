# Generated by Django 2.2.4 on 2019-10-07 13:43

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("froide_crowdfunding", "0007_auto_20190917_1046"),
    ]

    operations = [
        migrations.AddField(
            model_name="crowdfunding",
            name="amount_tentative",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0"), max_digits=10
            ),
        ),
    ]
