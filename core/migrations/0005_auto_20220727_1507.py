# Generated by Django 3.2 on 2022-07-27 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20220723_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='facebook_link',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='company',
            name='instagram_link',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='company',
            name='linkedin_link',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Linkedin'),
        ),
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='public/', verbose_name='Logo da empresa (ícone)'),
        ),
        migrations.AddField(
            model_name='company',
            name='name_logo',
            field=models.ImageField(blank=True, null=True, upload_to='public/', verbose_name='Logo do nome (menu)'),
        ),
        migrations.AddField(
            model_name='company',
            name='support_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email de atendimento'),
        ),
        migrations.AddField(
            model_name='company',
            name='support_phone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Telefone de atendimento'),
        ),
    ]