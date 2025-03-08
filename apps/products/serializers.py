from rest_framework import serializers
from .models import Category, Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Product Categories"""
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product Management"""
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        max_length=5  # Maximum 5 images
    )
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'seller', 
                 'stock', 'requires_shipping', 'weight', 'length', 'width', 
                 'height', 'free_shipping', 'created_at', 'updated_at', 
                 'images', 'uploaded_images']
        read_only_fields = ('seller',)

    def validate_uploaded_images(self, value):
        """Validate uploaded images"""
        print(f"Validating uploaded images: {value}")
        if len(value) > 5:
            raise serializers.ValidationError("You can upload a maximum of 5 images.")
        return value

    def create(self, validated_data):
        """Create a new product with images"""
        print(f"Creating product with data: {validated_data}")
        request = self.context.get('request')
        if request and request.user:
            validated_data['seller'] = request.user
            
        uploaded_images = validated_data.pop('uploaded_images', [])
        print(f"Uploaded images: {uploaded_images}")
        
        product = super().create(validated_data)
        
        for i, image in enumerate(uploaded_images):
            print(f"Creating image {i}: {image}")
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(i == 0)  # First image is primary
            )
        
        return product

    def update(self, instance, validated_data):
        """Update a product and its images"""
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = super().update(instance, validated_data)
        
        # Handle new images
        existing_images_count = product.images.count()
        if existing_images_count + len(uploaded_images) > 5:
            raise serializers.ValidationError({
                'uploaded_images': f'This product already has {existing_images_count} images. '
                                 f'You can only add {5 - existing_images_count} more.'
            })
            
        for image in uploaded_images:
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(not product.images.filter(is_primary=True).exists())
            )
        
        return product

    def validate(self, data):
        """Validate shipping-related fields"""
        requires_shipping = data.get('requires_shipping', True)  # Default to True if not provided
        
        if requires_shipping:
            shipping_fields = ['weight', 'length', 'width', 'height']
            missing_fields = [field for field in shipping_fields if not data.get(field)]
            
            if missing_fields:
                raise serializers.ValidationError({
                    field: 'This field is required when requires_shipping is True'
                    for field in missing_fields
                })
            
            # Validate minimum values
            for field in shipping_fields:
                value = data.get(field)
                if value and value <= 0:
                    raise serializers.ValidationError({
                        field: f"{field.title()} must be greater than 0"
                    })
        
        return data
