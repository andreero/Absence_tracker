# Generated by Django 4.0.5 on 2022-07-08 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('absences', '0006_alter_publicholiday_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicholiday',
            name='country',
            field=models.ForeignKey(db_column='CRY_COD', on_delete=django.db.models.deletion.CASCADE, related_name='holidays', to='accounts.country'),
        ),
    ]
