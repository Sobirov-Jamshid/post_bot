# Generated by Django 4.1.3 on 2022-12-15 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.channel'),
        ),
    ]