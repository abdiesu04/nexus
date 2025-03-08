from rest_framework import serializers
from .models import Order, Payment

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Creating and Viewing Orders"""
    id = serializers.UUIDField(read_only=True)  # Ensure UUID is read-only

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('buyer', 'total_price', 'status')

    def create(self, validated_data):
        """Ensure buyer is the logged-in user and calculate total price"""
        request = self.context['request']
        validated_data['buyer'] = request.user
        validated_data['total_price'] = validated_data['product'].price * validated_data['quantity']
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Managing Payments"""
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('payment_status', 'transaction_id')
