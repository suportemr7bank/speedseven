# Generated by Django 3.2 on 2022-06-15 19:15

from django.db import migrations, models
import django.db.models.deletion
import investment.interfaces.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investment', '0002_alter_bank_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fund_amount', models.FloatField(blank=True, null=True, validators=[investment.interfaces.validators.validate_null_or_greate_than_zero], verbose_name='Valor total do fundo')),
                ('min_deposit', models.FloatField(blank=True, help_text='Valor mínimo para investimento', null=True, validators=[investment.interfaces.validators.validate_null_or_greate_than_zero], verbose_name='Depósito mínimo')),
                ('application', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='crowdfunding_settings', to='investment.application', verbose_name='Aplicação')),
            ],
            options={
                'verbose_name': 'Configuração da aplicação',
                'verbose_name_plural': 'Configurações das aplicações',
            },
        ),
    ]