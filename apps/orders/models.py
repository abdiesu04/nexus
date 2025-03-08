from uuid import uuid4
from django.db import models
from apps.products.models import Product
from apps.authentication.models import User

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class Payment(models.Model):
    """Payment Model for Handling Transactions with a Required Transaction ID"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Can be null for pending, required for completed
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Ensure transaction_id is required for completed payments"""
        if self.payment_status == 'completed' and not self.transaction_id:
            raise ValueError("A completed payment must have a transaction ID.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.payment_status}"

