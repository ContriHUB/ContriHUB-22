# Generated by Django 4.1 on 2022-10-18 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0039_issueassignmentrequest_requested_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="bonus_pt",
            field=models.IntegerField(default=0, verbose_name="Bonus Points"),
        ),
    ]
