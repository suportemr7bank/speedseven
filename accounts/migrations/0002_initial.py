# Generated by Django 3.2 on 2022-06-06 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
        migrations.AddField(
            model_name='custominvitation',
            name='inviter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='apiaccess',
            name='operator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='user_operator', to=settings.AUTH_USER_MODEL, verbose_name='Operador'),
        ),
        migrations.AddField(
            model_name='apiaccess',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário e senha de acesso'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role'), name='unique_user_role_constraint'),
        ),
    ]