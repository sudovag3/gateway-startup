# Generated by Django 4.2.1 on 2023-05-25 15:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0006_rename_marr_review_mark_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contest',
            name='contest_admins',
        ),
        migrations.AlterField(
            model_name='contest',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='contests_participant', to=settings.AUTH_USER_MODEL, verbose_name='participants'),
        ),
        migrations.AddField(
            model_name='contest',
            name='contest_admins',
            field=models.ManyToManyField(blank=True, related_name='contests_admin', to=settings.AUTH_USER_MODEL, verbose_name='contest_admins'),
        ),
    ]
