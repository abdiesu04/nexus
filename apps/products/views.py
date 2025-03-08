from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters as django_filters
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for consistent pagination"""
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 100  # Maximum limit per page
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total number of items
            'next': self.get_next_link(),  # URL for next page
            'previous': self.get_previous_link(),  # URL for previous page
            'results': data  # Current page of results
        })

class ProductFilter(FilterSet):
    """Filter set for advanced product filtering"""
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category_name = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')
    seller_name = django_filters.CharFilter(field_name="seller__username", lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    requires_shipping = django_filters.BooleanFilter(field_name="requires_shipping")
    free_shipping = django_filters.BooleanFilter(field_name="free_shipping")
    
    class Meta:
        model = Product
        fields = {
            'title': ['icontains'],
            'description': ['icontains'],
            'stock': ['gte', 'lte'],
            'category': ['exact'],
            'seller': ['exact'],
        }

class IsSellerOrAdmin(permissions.BasePermission):
    """Custom permission to allow only sellers and admins to modify products."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["seller", "admin"]

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        if hasattr(obj, 'seller'):
            return obj.seller == request.user
        if hasattr(obj, 'product'):
            return obj.product.seller == request.user
        return False
    
class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD API for Product Categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """Define access rules"""
        if self.action in ['create', 'update', 'destroy']:
            return [IsSellerOrAdmin()]
        return [permissions.AllowAny()]  # Anyone can view categories
    
class ProductViewSet(viewsets.ModelViewSet):
    """CRUD API for Products with advanced search and filtering"""
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'category__name', 'seller__username']
    ordering_fields = ['price', 'created_at', 'stock', 'title']
    ordering = ['-created_at']  # Default ordering

    def get_permissions(self):
        """Define permission rules based on the action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'set_primary_image', 'delete_image']:
            return [IsSellerOrAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """Ensure the product is saved under the logged-in seller"""
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'])
    def set_primary_image(self, request, pk=None):
        """Set an image as primary for the product"""
        product = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            image = ProductImage.objects.get(id=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response(
                {'detail': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        image.is_primary = True
        image.save()
        
        serializer = ProductImageSerializer(image)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """Delete a product image"""
        product = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            image = ProductImage.objects.get(id=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response(
                {'detail': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        was_primary = image.is_primary
        image.delete()
        
        # If we deleted the primary image, set the first remaining image as primary
        if was_primary:
            first_image = product.images.first()
            if first_image:
                first_image.is_primary = True
                first_image.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

