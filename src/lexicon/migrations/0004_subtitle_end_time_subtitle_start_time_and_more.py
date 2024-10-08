# Generated by Django 4.0.5 on 2024-09-08 21:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0003_subtitle"),
    ]

    operations = [
        migrations.AddField(
            model_name="subtitle",
            name="end_time",
            field=models.TimeField(db_index=True, default=None, verbose_name="End time"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="subtitle",
            name="start_time",
            field=models.TimeField(db_index=True, default=None, verbose_name="Start time"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="subtitle",
            name="cc_subtitle",
            field=models.TextField(db_index=True, max_length=1024, verbose_name="CC subtitle"),
        ),
        migrations.AlterField(
            model_name="subtitle",
            name="language",
            field=models.CharField(db_index=True, max_length=50, verbose_name="language"),
        ),
        migrations.AlterField(
            model_name="subtitle",
            name="video",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="lexicon.video",
                verbose_name="video",
            ),
        ),
    ]
