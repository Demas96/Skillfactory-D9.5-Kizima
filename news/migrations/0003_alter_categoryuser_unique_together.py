# Generated by Django 4.0.3 on 2022-04-07 13:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0002_categoryuser_category_subscribers_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='categoryuser',
            unique_together={('user', 'category')},
        ),
    ]
