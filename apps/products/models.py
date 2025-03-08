from django.db import models
from apps.authentication.models import User
from uuid import uuid4
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Category(models.Model):
    """Product Categories (e.g., Skin Care, Fashion, Home & Decor)"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """Model for storing multiple images per product"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images of this product to not primary
            ProductImage.objects.filter(product=self.product).update(is_primary=False)
        super().save(*args, **kwargs)

class Product(models.Model):
    """Product Model for Sellers to List Items"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    
    # Shipping related fields
    requires_shipping = models.BooleanField(
        default=True,
        help_text="Whether this product needs to be shipped. Digital products should set this to False."
    )
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Weight in pounds (lb)", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01, message="Weight must be greater than 0")]
    )
    length = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Length in inches (in)", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01, message="Length must be greater than 0")]
    )
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Width in inches (in)", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01, message="Width must be greater than 0")]
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Height in inches (in)", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01, message="Height must be greater than 0")]
    )
    free_shipping = models.BooleanField(
        default=False,
        help_text="Whether shipping costs are included in the product price"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        """Validate shipping information"""
        if self.requires_shipping:
            shipping_fields = {'weight': self.weight, 'length': self.length, 
                             'width': self.width, 'height': self.height}
            missing_fields = [field for field, value in shipping_fields.items() if value is None]
            if missing_fields:
                raise ValidationError({
                    field: 'This field is required when requires_shipping is True'
                    for field in missing_fields
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_parcel_details(self):
        """Get parcel details for shipping calculations"""
        if not self.requires_shipping:
            raise ValueError("This product does not require shipping")
            
        if not all([self.length, self.width, self.height, self.weight]):
            raise ValueError("Product shipping dimensions are not complete")
            
        return {
            "length": float(self.length),
            "width": float(self.width),
            "height": float(self.height),
            "distance_unit": "in",
            "weight": float(self.weight),
            "mass_unit": "lb"
        }

