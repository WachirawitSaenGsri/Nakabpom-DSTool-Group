# Generated by Django 5.0.7 on 2025-02-26 12:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("demo", "0003_category_alter_order_customer_alter_order_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="img_product",
            field=models.ImageField(blank=True, null=True, upload_to="img/"),
        ),
    ]
