from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Order, Payment
from .serializers import OrderSerializer, PaymentSerializer
from uuid import uuid4

class IsBuyerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role in ['buyer', 'admin'])

class IsSellerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role in ['seller', 'admin'])

class OrderViewSet(viewsets.ModelViewSet):
    """API for Order Management in Marketplace"""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter orders based on user role"""
        user = self.request.user
        if user.role == 'admin':
            return Order.objects.all()
        elif user.role == 'buyer':
            return Order.objects.filter(buyer=user)
        elif user.role == 'seller':
            return Order.objects.filter(product__seller=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        """Ensure the buyer is the logged-in user"""
        if self.request.user.role != 'buyer':
            raise permissions.PermissionDenied("Only buyers can create orders")
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsSellerOrAdmin])
    def update_status(self, request, pk=None):
        """Update order status (Seller/Admin only)"""
        order = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[IsBuyerOrAdmin])
    def cancel(self, request, pk=None):
        """Cancel order (Buyer/Admin only)"""
        order = self.get_object()
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Cannot cancel order that has been shipped or delivered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)

class PaymentViewSet(viewsets.ModelViewSet):
    """API for Processing Payments"""
    serializer_class = PaymentSerializer
    permission_classes = [IsBuyerOrAdmin]
    queryset = Payment.objects.all()

    def get_queryset(self):
        """Filter payments based on user role"""
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        elif user.role == 'buyer':
            return Payment.objects.filter(order__buyer=user)
        return Payment.objects.none()

    def create(self, request, *args, **kwargs):
        """Process Payment for an Order"""
        order = get_object_or_404(Order, id=request.data.get('order'))
        
        # Verify buyer
        if request.user != order.buyer and not request.user.role == 'admin':
            raise permissions.PermissionDenied("You can only pay for your own orders")
            
        # Check if order is already paid
        if Payment.objects.filter(order=order, payment_status='completed').exists():
            return Response(
                {'error': 'Order is already paid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate payment gateway
        fake_transaction_id = str(uuid4())

        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            payment_status='completed',
            transaction_id=fake_transaction_id
        )

        # Update Order Status
        order.status = 'processing'
        order.save()
        
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)