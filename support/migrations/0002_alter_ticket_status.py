# Generated by Django 5.2.1 on 2025-05-12 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('assigned', 'Assigned'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', max_length=20),
        ),
    ]
