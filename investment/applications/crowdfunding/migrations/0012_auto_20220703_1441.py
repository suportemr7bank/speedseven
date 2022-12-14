# Generated by Django 3.2 on 2022-07-03 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0004_auto_20220620_2105'),
        ('crowdfunding', '0011_remove_applicationdeposit_requested'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicationdeposit',
            name='completed',
        ),
        migrations.AlterField(
            model_name='applicationdeposit',
            name='money_transfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='investment.moneytransfer', verbose_name='Operação de transferência'),
        ),
    ]
