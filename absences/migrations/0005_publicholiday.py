# Generated by Django 4.0.5 on 2022-07-08 10:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('absences', '0004_alter_absenceapprovalflowstatus_approval_flow_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='CLD_DAT')),
                ('description', models.CharField(db_column='HLD_DSC', max_length=255)),
                ('country', models.ForeignKey(db_column='CRY_COD', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
