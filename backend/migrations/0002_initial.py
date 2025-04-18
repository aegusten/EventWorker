# Generated by Django 5.2 on 2025-04-13 12:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('backend', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.applicant'),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.applicant'),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.organization'),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.jobposting'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.jobposting'),
        ),
        migrations.AddField(
            model_name='message',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.jobposting'),
        ),
        migrations.AddField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='users.organization'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='users.applicant'),
        ),
    ]
