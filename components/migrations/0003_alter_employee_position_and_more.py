# Generated by Django 5.0.3 on 2024-03-24 05:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("components", "0002_matirial_read_out_read_warehousing_read_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="position",
            field=models.CharField(
                choices=[
                    ("C", "总监"),
                    ("M", "经理"),
                    ("E", "工程师"),
                    ("T", "技术员"),
                    ("S", "员工"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="matirial",
            name="matirail_Qualify",
            field=models.CharField(max_length=50),
        ),
    ]
