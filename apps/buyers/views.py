from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination

from apps.orders.models import Order
from apps.products.models import Product
from .models import Wishlist
from .serializers import (
    BuyerOrderSerializer,
    BuyerDashboardStatsSerializer,
    WishlistProductSerializer,
    BuyerShippingSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsBuyerOrAdmin(permissions.BasePermission):
    """Permission class for buyer or admin access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['buyer', 'admin']
        
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        return False

class BuyerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsBuyerOrAdmin]
    pagination_class = StandardResultsSetPagination

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get buyer's dashboard statistics"""
        orders = Order.objects.filter(buyer=request.user)
        wishlist_count = Wishlist.objects.filter(buyer=request.user).count()
        
        # Calculate statistics
        stats = {
            'total_orders': orders.count(),
            'active_orders': orders.filter(
                status__in=['pending', 'processing', 'shipped']
            ).count(),
            'completed_orders': orders.filter(status='delivered').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'total_spent': orders.filter(
                payment__payment_status='completed'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'wishlist_count': wishlist_count
        }
        
        serializer = BuyerDashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def orders(self, request):
        """Get buyer's order history"""
        status_filter = request.query_params.get('status')
        date_filter = request.query_params.get('date')
        
        orders = Order.objects.filter(buyer=request.user)
        
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
            serializer = BuyerOrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BuyerOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_orders(self, request):
        """Get buyer's active orders"""
        orders = Order.objects.filter(
            buyer=request.user,
            status__in=['pending', 'processing', 'shipped']
        ).order_by('-created_at')

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = BuyerOrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BuyerOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def wishlist(self, request):
        """Get buyer's wishlist"""
        wishlist_items = Wishlist.objects.filter(buyer=request.user)
        
        page = self.paginate_queryset(wishlist_items)
        if page is not None:
            serializer = WishlistProductSerializer([item.product for item in page], many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WishlistProductSerializer([item.product for item in wishlist_items], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        """Add a product to wishlist"""
        try:
            product = Product.objects.get(id=pk)
            wishlist_item, created = Wishlist.objects.get_or_create(
                buyer=request.user,
                product=product
            )
            if created:
                return Response({'message': 'Product added to wishlist'})
            return Response(
                {'message': 'Product already in wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request, pk=None):
        """Remove a product from wishlist"""
        try:
            wishlist_item = Wishlist.objects.get(
                buyer=request.user,
                product_id=pk
            )
            wishlist_item.delete()
            return Response({'message': 'Product removed from wishlist'})
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Product not in wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )
