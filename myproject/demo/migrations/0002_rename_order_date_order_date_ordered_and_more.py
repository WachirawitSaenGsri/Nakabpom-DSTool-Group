# Generated by Django 5.0.7 on 2025-02-25 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("demo", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="order_date",
            new_name="date_ordered",
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("completed", "Completed")],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="orderdetail",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_details",
                to="demo.order",
            ),
        ),
        migrations.AlterField(
            model_name="orderdetail",
            name="quantity",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="product",
            name="stock",
            field=models.IntegerField(),
        ),
    ]
