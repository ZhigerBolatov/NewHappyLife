# Generated by Django 5.1.3 on 2024-11-28 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_alter_user_address_alter_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('AC', 'Accepted'), ('RJ', 'Rejected'), ('DN', 'Done')], default='AC', max_length=20),
        ),
    ]
