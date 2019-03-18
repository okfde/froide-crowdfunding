# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-24 17:29
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('foirequest', '0029_auto_20180924_1107'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('froide_payment', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('note', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Contribution',
                'verbose_name_plural': 'Contributions',
                'ordering': ('-timestamp',),
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.CreateModel(
            name='Crowdfunding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('needs_approval', 'needs approval'), ('denied', 'denied'), ('running', 'running'), ('finished', 'finished')], default='needs_approval', max_length=25)),
                ('kind', models.CharField(choices=[('fees', 'fees'), ('appeal', 'appeal'), ('lawsuit', 'lawsuit'), ('other', 'other')], max_length=25)),
                ('date_requested', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('date_approved', models.DateTimeField(blank=True, null=True)),
                ('date_end', models.DateTimeField(blank=True, null=True)),
                ('amount_requested', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_needed', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_raised', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='foirequest.FoiRequest')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Crowdfunding',
                'verbose_name_plural': 'Crowdfundings',
                'ordering': ('-date_requested',),
                'get_latest_by': 'date_requested',
            },
        ),
        migrations.AddField(
            model_name='contribution',
            name='crowdfunding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='froide_crowdfunding.Crowdfunding'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='froide_payment.Order'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]