from django.db import models
from uuid import uuid4
from apps.authentication.models import User
from apps.products.models import Product

class Wishlist(models.Model):
    """Wishlist model for buyers to save products for later"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['buyer', 'product']  # Prevent duplicate wishlist entries
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.buyer.email}'s wishlist item: {self.product.title}"
