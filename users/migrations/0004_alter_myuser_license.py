# Generated by Django 3.2.9 on 2022-06-07 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_myuser_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='license',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.license'),
        ),
    ]