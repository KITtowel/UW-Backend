# Generated by Django 4.1.7 on 2023-05-16 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_withdrawal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='nickname',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
