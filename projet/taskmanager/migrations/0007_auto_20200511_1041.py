# Generated by Django 2.1.15 on 2020-05-11 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0006_task_last_modification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='last_modification',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
