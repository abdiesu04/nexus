from rest_framework import serializers
from apps.products.models import Product
from apps.orders.models import Order, Payment
from apps.shipping.models import Shipping

class DashboardProductSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'stock',
            'category', 'created_at', 'updated_at', 'image',
            'total_orders', 'revenue',
            # Shipping related fields
            'weight', 'length', 'width', 'height',
            'free_shipping', 'requires_shipping'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DashboardOrderSerializer(serializers.ModelSerializer):
    product = DashboardProductSerializer(read_only=True)
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    payment_status = serializers.CharField(source='payment.payment_status', read_only=True)
    shipping_status = serializers.CharField(source='shipping.status', read_only=True)
    tracking_number = serializers.CharField(source='shipping.tracking_number', read_only=True)
    shipping_label_url = serializers.URLField(source='shipping.label_url', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product', 'buyer_name', 'buyer_email',
            'quantity', 'total_price', 'status', 'payment_status',
            'shipping_status', 'tracking_number', 'shipping_label_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DashboardPaymentSerializer(serializers.ModelSerializer):
    order = DashboardOrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_status',
            'transaction_id', 'created_at'
        ]
        read_only_fields = ['created_at']

class DashboardShippingSerializer(serializers.ModelSerializer):
    order = DashboardOrderSerializer(read_only=True)
    
    class Meta:
        model = Shipping
        fields = [
            'id', 'order', 'tracking_number', 'tracking_url',
            'label_url', 'carrier', 'shipping_method', 'shipping_cost',
            'status', 'created_at', 'updated_at', 'shipped_at',
            'delivered_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DashboardStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField() 