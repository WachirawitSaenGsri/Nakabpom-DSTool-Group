# Generated by Django 5.0.7 on 2025-02-26 19:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("demo", "0006_alter_payment_method"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Preparation", "Preparation"),
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("canceled", "Canceled"),
                ],
                default="Preparation",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="method",
            field=models.CharField(choices=[("cash", "Cash")], max_length=10),
        ),
    ]
