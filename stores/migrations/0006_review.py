# Generated by Django 4.1.7 on 2023-05-01 00:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_withdrawal'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0005_storedaegu_likes_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200)),
                ('rating', models.FloatField(validators=[django.core.validators.MaxValueValidator(5.0)])),
                ('published_data', models.DateTimeField(default=django.utils.timezone.now)),
                ('reported_num', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='stores.storedaegu')),
            ],
        ),
    ]
