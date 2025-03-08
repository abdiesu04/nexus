        from rest_framework import serializers
        from .models import SellerAddress, BuyerAddress, Shipping, ShippingStatusHistory
        from django.core.exceptions import ValidationError

        class SellerAddressSerializer(serializers.ModelSerializer):
            class Meta:
                model = SellerAddress
                fields = [
                    'id', 'name', 'company', 'street1', 'street2', 'city', 'state',
                    'zip_code', 'country', 'phone', 'email', 'is_default', 'is_verified',
                    'is_warehouse', 'warehouse_hours', 'created_at', 'updated_at'
                ]
                read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

            def validate(self, data):
                """
                Validate the address data before saving
                """
                # Clean phone number - remove special characters
                if 'phone' in data:
                    data['phone'] = ''.join(filter(str.isdigit, data['phone']))
                    if len(data['phone']) < 10:
                        raise serializers.ValidationError({
                            'phone': 'Phone number must have at least 10 digits'
                        })
                
                # Ensure country is uppercase
                if 'country' in data:
                    data['country'] = data['country'].upper()
                
                # Ensure required fields are not empty strings
                required_fields = ['name', 'street1', 'city', 'state', 'zip_code']
                for field in required_fields:
                    if field in data and not data[field].strip():
                        raise serializers.ValidationError({
                            field: f'{field} cannot be empty'
                        })
                
                return data

            def create(self, validated_data):
                # Set seller from context
                validated_data['seller'] = self.context['request'].user
                try:
                    return super().create(validated_data)
                except ValidationError as e:
                    raise serializers.ValidationError(e.message_dict)

        class BuyerAddressSerializer(serializers.ModelSerializer):
            class Meta:
                model = BuyerAddress
                fields = [
                    'id', 'name', 'company', 'street1', 'street2', 'city', 'state',
                    'zip_code', 'country', 'phone', 'email', 'is_default', 'is_verified',
                    'is_residential', 'delivery_instructions', 'created_at', 'updated_at'
                ]
                read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

            def validate(self, data):
                """
                Validate the address data before saving
                """
                # Clean phone number - remove special characters
                if 'phone' in data:
                    data['phone'] = ''.join(filter(str.isdigit, data['phone']))
                    if len(data['phone']) < 10:
                        raise serializers.ValidationError({
                            'phone': 'Phone number must have at least 10 digits'
                        })
                
                # Ensure country is uppercase
                if 'country' in data:
                    data['country'] = data['country'].upper()
                
                # Ensure required fields are not empty strings
                required_fields = ['name', 'street1', 'city', 'state', 'zip_code']
                for field in required_fields:
                    if field in data and not data[field].strip():
                        raise serializers.ValidationError({
                            field: f'{field} cannot be empty'
                        })

                # Convert state abbreviation to full name if needed
                state_mapping = {
                    'CA': 'California',
                    'NY': 'New York',
                    # Add more state mappings as needed
                }
                if 'state' in data and data['state'].upper() in state_mapping:
                    data['state'] = state_mapping[data['state'].upper()]
                
                return data

            def create(self, validated_data):
                # Set buyer from context
                validated_data['buyer'] = self.context['request'].user
                
                # Handle is_default flag
                is_default = validated_data.get('is_default', False)
                if is_default:
                    # If this address is being set as default, unset any existing default
                    BuyerAddress.objects.filter(
                        buyer=validated_data['buyer'],
                        is_default=True
                    ).update(is_default=False)
                elif not BuyerAddress.objects.filter(buyer=validated_data['buyer']).exists():
                    # If this is the first address for the buyer, make it default
                    validated_data['is_default'] = True
                
                try:
                    return super().create(validated_data)
                except ValidationError as e:
                    raise serializers.ValidationError(e.message_dict)
                except Exception as e:
                    raise serializers.ValidationError({
                        'error': str(e)
                    })

        class ShippingStatusHistorySerializer(serializers.ModelSerializer):
            class Meta:
                model = ShippingStatusHistory
                fields = ['id', 'status', 'location', 'description', 'created_at']
                read_only_fields = ['id', 'created_at']

        class ShippingSerializer(serializers.ModelSerializer):
            from_address = SellerAddressSerializer(read_only=True)
            to_address = BuyerAddressSerializer(read_only=True)
            status_history = ShippingStatusHistorySerializer(many=True, read_only=True)
            
            class Meta:
                model = Shipping
                fields = [
                    'id', 'order', 'from_address', 'to_address', 'shippo_transaction_id',
                    'tracking_number', 'tracking_url', 'label_url', 'carrier',
                    'shipping_method', 'shipping_cost', 'estimated_delivery_date',
                    'status', 'status_history', 'created_at', 'updated_at',
                    'shipped_at', 'delivered_at'
                ]
                read_only_fields = [
                    'id', 'shippo_transaction_id', 'tracking_number', 'tracking_url',
                    'label_url', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
                ]

        class ShippingRateSerializer(serializers.Serializer):
            provider = serializers.CharField()
            service = serializers.CharField(source='servicelevel.name')
            amount = serializers.DecimalField(max_digits=10, decimal_places=2)
            currency = serializers.CharField()
            duration_terms = serializers.CharField()
            rate_id = serializers.CharField(source='object_id')
            estimated_days = serializers.IntegerField(source='days', required=False)
            provider_image_75 = serializers.URLField(required=False)
            provider_image_200 = serializers.URLField(required=False)

            def to_representation(self, instance):
                """Custom representation of shipping rate data"""
                data = super().to_representation(instance)
                
                # Handle missing fields gracefully
                if not data.get('service') and hasattr(instance, 'servicelevel'):
                    data['service'] = getattr(instance.servicelevel, 'name', 'Standard')
                elif not data.get('service'):
                    data['service'] = 'Standard'
                    
                if not data.get('duration_terms'):
                    data['duration_terms'] = 'Delivery time varies'
                    
                if not data.get('estimated_days'):
                    data['estimated_days'] = None
                    
                return data

        class AddressValidationSerializer(serializers.Serializer):
            is_valid = serializers.BooleanField()
            messages = serializers.ListField(child=serializers.CharField(), required=False)
            address = serializers.DictField(required=False) 