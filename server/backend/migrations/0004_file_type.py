# Generated by Django 4.1.3 on 2022-12-14 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_information_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='type',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]