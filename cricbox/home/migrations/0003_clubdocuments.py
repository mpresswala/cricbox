# Generated by Django 3.1.5 on 2021-03-03 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_add_sql_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('document', models.FileField(upload_to='uploads/%Y/%m/%d/')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
