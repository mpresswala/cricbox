# Generated by Django 3.1.5 on 2021-02-22 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0002_auto_20210222_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, verbose_name='Remarks'),
        ),
    ]