# Generated by Django 5.1.3 on 2024-11-25 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_user_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='week_day',
            field=models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=10),
        ),
    ]
