# Generated by Django 4.1.7 on 2023-05-01 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0006_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
