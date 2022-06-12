# Generated by Django 4.0.5 on 2022-06-08 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('absences', '0006_alter_absence_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='approval_comment',
            field=models.TextField(blank=True, db_column='APR_CMT', default=str, null=True),
        ),
        migrations.AlterField(
            model_name='absence',
            name='approval_message',
            field=models.JSONField(blank=True, db_column='APR_MSG', default=str, null=True),
        ),
        migrations.AlterField(
            model_name='absence',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_column='T_REC_SRC_TST', null=True),
        ),
    ]
