# Generated by Django 2.2.4 on 2019-10-07 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('froide_crowdfunding', '0008_crowdfunding_amount_tentative'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrowdfundingProgressCMSPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='froide_crowdfunding_crowdfundingprogresscmsplugin', serialize=False, to='cms.CMSPlugin')),
                ('crowdfunding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='froide_crowdfunding.Crowdfunding')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='CrowdfundingFormCMSPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='froide_crowdfunding_crowdfundingformcmsplugin', serialize=False, to='cms.CMSPlugin')),
                ('crowdfunding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='froide_crowdfunding.Crowdfunding')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]