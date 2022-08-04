# Generated by Django 3.2 on 2022-06-19 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0003_alter_application_is_active'),
        ('crowdfunding', '0002_pendingdeposit'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationsettings',
            name='state',
            field=models.CharField(choices=[('OP', 'Aberto para contratação'), ('OD', 'Aguardando aportes'), ('CO', 'Fundo finalizado (captação concluída)'), ('CA', 'Fundo cancelado')], default='OP', max_length=2, verbose_name='Situação'),
        ),
        migrations.AlterField(
            model_name='pendingdeposit',
            name='application_account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='investment.applicationaccount', verbose_name='Conta do cliente'),
        ),
    ]
