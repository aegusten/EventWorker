# Generated by Django 5.2 on 2025-04-14 02:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_applicant_table_alter_organization_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicant',
            name='account_status',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='account_status',
        ),
    ]
