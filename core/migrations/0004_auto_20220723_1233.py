# Generated by Django 3.2 on 2022-07-23 15:33

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20220722_1752'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1024, verbose_name='Questão')),
                ('answer', tinymce.models.HTMLField(verbose_name='Resposta')),
                ('order', models.PositiveIntegerField(verbose_name='Ordem de exibição')),
            ],
        ),
        migrations.CreateModel(
            name='FAQConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Título da página')),
                ('target_page', models.CharField(blank=True, choices=[('PUB', 'Pública'), ('CLI', 'Cliente')], max_length=3, null=True, verbose_name='Página')),
            ],
        ),
        migrations.AddConstraint(
            model_name='faqconfig',
            constraint=models.UniqueConstraint(fields=('target_page',), name='unique_faq_config_constraint'),
        ),
        migrations.AddField(
            model_name='faq',
            name='faq_config',
            field=models.ManyToManyField(blank=True, to='core.FAQConfig', verbose_name='Página de exibição'),
        ),
    ]