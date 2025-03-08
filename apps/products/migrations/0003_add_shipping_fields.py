from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_product_free_shipping_product_requires_shipping'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Height in inches (in)', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Length in inches (in)', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Weight in pounds (lb)', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Width in inches (in)', max_digits=10, null=True),
        ),
    ] 