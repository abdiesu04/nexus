from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.utils import timezone
from apps.orders.models import Order
from .models import Shipping, SellerAddress, BuyerAddress, ShippingStatusHistory
from .serializers import (
    ShippingSerializer, SellerAddressSerializer, BuyerAddressSerializer,
    ShippingRateSerializer, AddressValidationSerializer
)
from datetime import datetime
from django.conf import settings
import logging
import shippo
from shippo.models import components

# Set up logger
logger = logging.getLogger(__name__)

# Initialize Shippo
logger.info(f"Initializing Shippo with API key: {settings.SHIPPO_API_KEY[:6]}...")
shippo_sdk = shippo.Shippo(api_key_header=settings.SHIPPO_API_KEY)

# Log available Shippo modules
logger.info(f"Available Shippo attributes: {dir(shippo)}")

class IsSellerOrAdmin(BasePermission):
    """Permission class for seller or admin access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['seller', 'admin']
        
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'seller'):
            return obj.seller == request.user
        if hasattr(obj, 'order'):
            return obj.order.product.seller == request.user
        return False

class IsBuyerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['buyer', 'admin']
        
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        return False

class SellerAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing seller addresses"""
    serializer_class = SellerAddressSerializer
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]

    def get_queryset(self):
        return SellerAddress.objects.filter(seller=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set an address as default"""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'status': 'Default address set.'})

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate address with Shippo"""
        address = self.get_object()
        validation_results = address.validate_address()
        if validation_results:
            serializer = AddressValidationSerializer(validation_results)
            return Response(serializer.data)
        return Response(
            {'error': 'Address validation failed'},
            status=status.HTTP_400_BAD_REQUEST
        )

class BuyerAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing buyer addresses"""
    serializer_class = BuyerAddressSerializer
    permission_classes = [IsAuthenticated, IsBuyerOrAdmin]

    def get_queryset(self):
        return BuyerAddress.objects.filter(buyer=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set an address as default"""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'status': 'Default address set.'})

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate address with Shippo"""
        address = self.get_object()
        validation_results = address.validate_address()
        if validation_results:
            serializer = AddressValidationSerializer(validation_results)
            return Response(serializer.data)
        return Response(
            {'error': 'Address validation failed'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_shipping_rates(request):
    """Calculate shipping rates for an order"""
    try:
        order_id = request.data.get('order_id')
        logger.info(f"Calculating shipping rates for order: {order_id}")
        
        order = get_object_or_404(Order, id=order_id)
        
        # Allow both buyer and seller to calculate rates
        if (request.user != order.buyer and 
            request.user != order.product.seller and 
            request.user.role != 'admin'):
            return Response(
                {'error': 'You do not have permission to access this order'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get addresses
        from_address_id = request.data.get('from_address_id')
        to_address_id = request.data.get('to_address_id')
        
        if not from_address_id or not to_address_id:
            return Response(
                {'error': 'Both from_address_id and to_address_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get addresses from database
            from_address = get_object_or_404(SellerAddress, id=from_address_id, seller=order.product.seller)
            to_address = get_object_or_404(BuyerAddress, id=to_address_id, buyer=order.buyer)

            # Get product dimensions
            product = order.product
            try:
                # Validate product dimensions exist
                if not all([product.length, product.width, product.height, product.weight]):
                    return Response(
                        {
                            'error': 'Product dimensions are incomplete',
                            'details': 'Please ensure length, width, height, and weight are set for the product'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Convert dimensions to strings as required by Shippo
                dimensions = {
                    'length': str(float(product.length)),
                    'width': str(float(product.width)),
                    'height': str(float(product.height)),
                    'weight': str(float(product.weight))
                }
                
                logger.info(f"Product dimensions: {dimensions}")
            except (TypeError, ValueError) as e:
                logger.error(f"Error converting product dimensions: {str(e)}")
                return Response(
                    {
                        'error': 'Invalid product dimensions',
                        'details': 'Product dimensions must be valid numbers'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Create sender address in Shippo
                logger.info("Creating sender address in Shippo...")
                from_address_data = from_address.to_shippo_dict()
                logger.info(f"From address data: {from_address_data}")
                shippo_from_address = shippo_sdk.addresses.create(from_address_data)
                logger.info(f"Sender address created with ID: {shippo_from_address.object_id}")

                # Create recipient address in Shippo
                logger.info("Creating recipient address in Shippo...")
                to_address_data = to_address.to_shippo_dict()
                logger.info(f"To address data: {to_address_data}")
                shippo_to_address = shippo_sdk.addresses.create(to_address_data)
                logger.info(f"Recipient address created with ID: {shippo_to_address.object_id}")

                # Create parcel
                logger.info("Creating parcel in Shippo...")
                parcel_data = components.ParcelCreateRequest(
                    length=dimensions['length'],
                    width=dimensions['width'],
                    height=dimensions['height'],
                    distance_unit="in",
                    weight=dimensions['weight'],
                    mass_unit="lb"
                )
                logger.info(f"Parcel data: {parcel_data}")
                parcel = shippo_sdk.parcels.create(parcel_data)
                logger.info(f"Parcel created with ID: {parcel.object_id}")

                # Create shipment
                logger.info("Creating shipment in Shippo...")
                shipment_data = components.ShipmentCreateRequest(
                    address_from=shippo_from_address.object_id,
                    address_to=shippo_to_address.object_id,
                    parcels=[parcel.object_id],
                    async_=False
                )
                logger.info(f"Shipment data: {shipment_data}")
                shipment = shippo_sdk.shipments.create(shipment_data)
                logger.info(f"Shipment created with ID: {shipment.object_id}")

                # Get rates
                rates = shipment.rates
                if not rates:
                    logger.error("No rates available for shipment")
                    return Response(
                        {
                            'error': 'No shipping rates available',
                            'details': 'No carriers available for this route and parcel'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Log available rates
                logger.info(f"Retrieved {len(rates)} rates")
                for rate in rates:
                    logger.info(f"Rate: {rate.provider} - {rate.servicelevel.name} - ${rate.amount}")

                # Create or update shipping record
                shipping, created = Shipping.objects.get_or_create(
                    order=order,
                    defaults={
                        'from_address': from_address,
                        'to_address': to_address,
                        'carrier': 'pending',
                        'shipping_method': 'pending',
                        'shipping_cost': 0.00
                    }
                )

                if not created:
                    shipping.from_address = from_address
                    shipping.to_address = to_address
                    shipping.save()

                # Serialize and return rates
                serializer = ShippingRateSerializer(rates, many=True)
                
                return Response({
                    'shipping_id': shipping.id,
                    'rates': serializer.data
                })

            except Exception as e:
                logger.error(f"Error in Shippo API operations: {str(e)}", exc_info=True)
                return Response(
                    {
                        'error': 'Failed to process shipping with Shippo',
                        'details': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error getting addresses: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to get addresses',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Error in calculate_shipping_rates: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Failed to process shipping rate request',
                'details': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSellerOrAdmin])
def create_shipping_label(request, shipping_id):
    """Create shipping label for an order (Seller/Admin only)"""
    try:
        logger.info(f"Starting shipping label creation for shipping_id: {shipping_id}")
        logger.info(f"Request data: {request.data}")
        
        shipping = get_object_or_404(Shipping, id=shipping_id)
        order = shipping.order

        # Log request user and order details
        logger.info(f"Request user: {request.user.id}, Order seller: {order.product.seller.id}")

        # Verify the user is the seller of the product or an admin
        if request.user != order.product.seller and request.user.role != 'admin':
            logger.warning(f"Permission denied: User {request.user.id} attempted to create label for order {order.id}")
            return Response(
                {'error': 'Only the seller of this product or an admin can create shipping labels'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify order is paid
        if not hasattr(order, 'payment') or order.payment.payment_status != 'completed':
            return Response(
                {'error': 'Cannot create shipping label for unpaid order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get rate ID and details from request
        rate_id = request.data.get('rate_id')
        logger.info(f"Rate ID from request: {rate_id}")
        
        if not rate_id:
            logger.warning("No rate_id provided in request")
            return Response(
                {'error': 'Shipping rate ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify product has dimensions
        product = order.product
        logger.info(f"Product dimensions - L:{product.length}, W:{product.width}, H:{product.height}, Weight:{product.weight}")
        if not all([product.length, product.width, product.height, product.weight]):
            logger.error("Product missing shipping dimensions")
            return Response(
                {'error': 'Product shipping dimensions are incomplete'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify addresses exist
        if not shipping.from_address or not shipping.to_address:
            logger.error("Missing shipping addresses")
            return Response(
                {'error': 'Shipping addresses are not properly set'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create shipping label
        logger.info("Attempting to create Shippo label...")
        success, transaction, error_msg = shipping.create_shippo_label(rate_id)
        
        if success:
            logger.info(f"Label created successfully. Transaction ID: {transaction.object_id}")
            # Update shipping record with selected rate details
            shipping.carrier = transaction.rate.provider
            shipping.shipping_method = transaction.rate.servicelevel.name
            shipping.shipping_cost = transaction.rate.amount
            shipping.shippo_rate_id = rate_id
            shipping.save()

            # Update order status
            order.status = 'processing'
            order.save()
            
            # Create shipping status history
            ShippingStatusHistory.objects.create(
                shipping=shipping,
                status='PENDING',
                description='Shipping label created'
            )

            return Response({
                'message': 'Shipping label created successfully',
                'shipping_id': shipping.id,
                'tracking_number': shipping.tracking_number,
                'tracking_url': shipping.tracking_url,
                'label_url': shipping.label_url,
                'rate_details': {
                    'carrier': shipping.carrier,
                    'method': shipping.shipping_method,
                    'cost': shipping.shipping_cost
                }
            })
        else:
            logger.error(f"Failed to create Shippo label: {error_msg}")
            return Response(
                {'error': error_msg or 'Failed to create shipping label'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Error creating shipping label: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Failed to create shipping label',
                'details': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_shipment(request, shipping_id):
    """Track shipment status"""
    try:
        shipping = get_object_or_404(Shipping, id=shipping_id)
        order = shipping.order

        # Check permissions
        if (request.user != order.buyer and 
            request.user != order.product.seller and 
            request.user.role != 'admin'):
            return Response(
                {'error': 'You do not have permission to track this shipment'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get tracking information
        serializer = ShippingSerializer(shipping)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error tracking shipment: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Failed to track shipment',
                'details': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
