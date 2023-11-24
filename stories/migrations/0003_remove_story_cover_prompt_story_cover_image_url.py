# Generated by Django 4.2.7 on 2023-11-24 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0002_auto_20231111_1435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='cover_prompt',
        ),
        migrations.AddField(
            model_name='story',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
