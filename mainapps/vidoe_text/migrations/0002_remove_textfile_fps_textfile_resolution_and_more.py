# Generated by Django 4.2.16 on 2024-12-10 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vidoe_text', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textfile',
            name='fps',
        ),
        migrations.AddField(
            model_name='textfile',
            name='resolution',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='textfile',
            name='font',
            field=models.CharField(blank=True, default='Arial', max_length=50, null=True),
        ),
    ]
