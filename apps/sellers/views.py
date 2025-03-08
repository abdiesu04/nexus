from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination

from apps.products.models import Product
from apps.orders.models import Order, Payment
from apps.shipping.models import Shipping
from .serializers import (
    DashboardProductSerializer,
    DashboardOrderSerializer,
    DashboardPaymentSerializer,
    DashboardShippingSerializer,
    DashboardStatsSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsSellerOrAdmin(permissions.BasePermission):
    """Permission class for seller or admin access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['seller', 'admin']
        
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'seller'):
            return obj.seller == request.user
        if hasattr(obj, 'product'):
            return obj.product.seller == request.user
        return False

class SellerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsSellerOrAdmin]
    pagination_class = StandardResultsSetPagination

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get seller's dashboard statistics"""
        # Get seller's products
        products = Product.objects.filter(seller=request.user)
        
        # Get orders for seller's products
        orders = Order.objects.filter(product__in=products)
        
        # Calculate statistics
        stats = {
            'total_products': products.count(),
            'total_orders': orders.count(),
            'total_revenue': orders.filter(
                payment__payment_status='completed'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'pending_orders': orders.filter(status='pending').count(),
            'processing_orders': orders.filter(status='processing').count(),
            'shipped_orders': orders.filter(status='shipped').count(),
            'delivered_orders': orders.filter(status='delivered').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def products(self, request):
        """Get seller's products with order statistics"""
        products = Product.objects.filter(seller=request.user).annotate(
            total_orders=Count('orders'),
            revenue=Sum('orders__total_price', filter=Q(orders__payment__payment_status='completed'))
        )

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = DashboardProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DashboardProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def orders(self, request):
        """Get orders for seller's products"""
        status_filter = request.query_params.get('status')
        date_filter = request.query_params.get('date')
        
        orders = Order.objects.filter(product__seller=request.user)
        
        # Apply filters
        if status_filter:
            orders = orders.filter(status=status_filter)
            
        if date_filter:
            if date_filter == 'today':
                orders = orders.filter(created_at__date=timezone.now().date())
            elif date_filter == 'week':
                orders = orders.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                )
            elif date_filter == 'month':
                orders = orders.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                )

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = DashboardOrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DashboardOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def payments(self, request):
        """Get payments for seller's orders"""
        status_filter = request.query_params.get('status')
        
        payments = Payment.objects.filter(
            order__product__seller=request.user
        )
        
        if status_filter:
            payments = payments.filter(payment_status=status_filter)
            
        serializer = DashboardPaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def shipments(self, request):
        """Get shipping information for seller's orders"""
        status_filter = request.query_params.get('status')
        
        shipments = Shipping.objects.filter(
            order__product__seller=request.user
        )
        
        if status_filter:
            shipments = shipments.filter(status=status_filter)
            
        serializer = DashboardShippingSerializer(shipments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_order_status(self, request, pk=None):
        """Update order status"""
        try:
            order = Order.objects.get(
                id=pk,
                product__seller=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        new_status = request.data.get('status')
        if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = new_status
        order.save()
        
        serializer = DashboardOrderSerializer(order)
        return Response(serializer.data)
