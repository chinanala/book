# Generated by Django 3.1.1 on 2020-10-10 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('usr', models.CharField(max_length=20, unique=True)),
                ('pwd', models.CharField(max_length=20)),
            ],
        ),
    ]
