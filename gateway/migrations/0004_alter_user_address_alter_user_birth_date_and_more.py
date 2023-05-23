# Generated by Django 4.2.1 on 2023-05-23 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0003_alter_user_address_alter_user_birth_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='birth_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='contests',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gateway.contest'),
        ),
        migrations.AlterField(
            model_name='user',
            name='number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(blank=True, choices=[('CRE', 'CREATED'), ('COM', 'COMPLETED'), ('DEL', 'DELETED')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscribes',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gateway.subscribe'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tags',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_to_tag', to='gateway.tag'),
        ),
    ]
