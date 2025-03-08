from rest_framework import serializers
from apps.products.models import Product
from apps.orders.models import Order, Payment
from apps.shipping.models import Shipping

class WishlistProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price',
            'stock', 'category', 'image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class BuyerOrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'price', 'image',
            'seller'
        ]

class BuyerOrderSerializer(serializers.ModelSerializer):
    product = BuyerOrderProductSerializer(read_only=True)
    payment_status = serializers.CharField(source='payment.payment_status', read_only=True)
    shipping_status = serializers.CharField(source='shipping.status', read_only=True)
    tracking_number = serializers.CharField(source='shipping.tracking_number', read_only=True)
    tracking_url = serializers.URLField(source='shipping.tracking_url', read_only=True)
    estimated_delivery_date = serializers.DateField(source='shipping.estimated_delivery_date', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product', 'quantity', 'total_price',
            'status', 'payment_status', 'shipping_status',
            'tracking_number', 'tracking_url', 'estimated_delivery_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class BuyerDashboardStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    active_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    wishlist_count = serializers.IntegerField()

class BuyerShippingSerializer(serializers.ModelSerializer):
    order = BuyerOrderSerializer(read_only=True)
    
    class Meta:
        model = Shipping
        fields = [
            'id', 'order', 'tracking_number', 'tracking_url',
            'carrier', 'shipping_method', 'shipping_cost',
            'status', 'estimated_delivery_date',
            'created_at', 'updated_at', 'shipped_at',
            'delivered_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 