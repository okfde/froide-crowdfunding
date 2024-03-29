# Generated by Django 2.1.7 on 2019-03-15 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("froide_crowdfunding", "0002_auto_20190311_1528"),
    ]

    operations = [
        migrations.AddField(
            model_name="contribution",
            name="status",
            field=models.CharField(
                choices=[
                    ("", "Waiting for input"),
                    ("pending", "Processing..."),
                    ("success", "Successful"),
                    ("failed", "Failed"),
                ],
                default="",
                max_length=20,
            ),
        ),
    ]
