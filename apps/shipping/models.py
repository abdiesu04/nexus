from django.db import models  # Import Django's model system for database operations
from django.core.exceptions import ValidationError  # Import ValidationError for handling validation errors
from uuid import uuid4  # Import uuid4 for generating unique IDs
import shippo  # Import Shippo SDK for shipping functionality
from shippo.models import components  # Import Shippo components for creating shipping requests
from django.conf import settings  # Import Django settings to access configuration variables
from django.db.models.signals import pre_save  # Import pre_save signal for validation before saving
from django.dispatch import receiver  # Import receiver decorator for connecting signals
import logging  # Import logging for error tracking and debugging

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Initialize Shippo SDK with API key from settings
shippo_sdk = shippo.Shippo(api_key_header=settings.SHIPPO_API_KEY)

class Address(models.Model):
    """Abstract base class for addresses - provides common fields and methods for address models"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)  # Unique identifier for each address
    name = models.CharField(max_length=255)  # Full name of the person at this address
    company = models.CharField(max_length=255, blank=True, null=True)  # Optional company name
    street1 = models.CharField(max_length=255)  # Primary street address
    street2 = models.CharField(max_length=255, blank=True, null=True)  # Optional secondary address line
    city = models.CharField(max_length=255)  # City name
    state = models.CharField(max_length=255)  # State/province name
    zip_code = models.CharField(max_length=20)  # Postal/ZIP code
    country = models.CharField(max_length=2, default='US')  # Two-letter country code
    phone = models.CharField(max_length=20)  # Contact phone number
    email = models.EmailField()  # Contact email address
    is_default = models.BooleanField(default=False)  # Whether this is the default address
    is_verified = models.BooleanField(default=False)  # Whether address has been verified by Shippo
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when address was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when address was last updated

    class Meta:
        abstract = True  # Makes this an abstract base class - can't be instantiated directly

    def to_shippo_dict(self):
        """Convert Django address model to Shippo address format
        Returns a Shippo AddressCreateRequest object"""
        # Clean and format address components
        state_mapping = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
        
        # Clean state abbreviation
        state = self.state.strip().upper()
        if state in state_mapping:
            state = state_mapping[state]
        else:
            state = self.state.strip()
            
        # Clean street address - expand common abbreviations
        street_abbrev = {
            'ST.': 'STREET', 'ST ': 'STREET ', 'RD.': 'ROAD', 'RD ': 'ROAD ',
            'AVE.': 'AVENUE', 'AVE ': 'AVENUE ', 'BLVD.': 'BOULEVARD', 'BLVD ': 'BOULEVARD ',
            'LN.': 'LANE', 'LN ': 'LANE ', 'DR.': 'DRIVE', 'DR ': 'DRIVE '
        }
        street1 = self.street1.strip()
        for abbr, full in street_abbrev.items():
            street1 = street1.replace(abbr, full)
            
        # Format zip code
        zip_code = self.zip_code.strip()
        if len(zip_code) > 5:
            zip_code = zip_code[:5]  # Use only first 5 digits
            
        # Create the AddressCreateRequest object
        address_data = components.AddressCreateRequest(
            name=self.name.strip(),
            street1=street1,
            city=self.city.strip(),
            state=state,
            zip=zip_code,
            country=self.country.strip().upper(),
            phone=self.phone.strip(),
            email=self.email.strip(),
            company=self.company.strip() if self.company else None,
            street2=self.street2.strip() if self.street2 else None,
            validate=False  # Don't validate immediately
        )
        
        # Add residential flag if available
        if hasattr(self, 'is_residential'):
            address_data.residential = self.is_residential
            
        return address_data

    def validate_address(self):
        """Validate address using Shippo's address validation service
        Returns dictionary with validation results and any error messages"""
        try:
            # Create address data dictionary for validation
            address_data = self.to_shippo_dict()
            
            # First create the address in Shippo without validation
            address = shippo_sdk.addresses.create(address_data)
            
            # For residential addresses, we'll be more lenient
            is_residential = hasattr(self, 'is_residential') and self.is_residential
            
            if is_residential:
                logger.info(f"Processing residential address validation: {self.street1}, {self.city}, {self.state}")
                # For residential addresses, we'll accept it with a warning
                return {
                    'is_valid': True,
                    'messages': ['Address accepted as residential - validation skipped']
                }
            
            # For commercial addresses, perform strict validation
            try:
                validation = shippo_sdk.addresses.validate(address.object_id)
                
                if hasattr(validation, 'validation_results'):
                    is_valid = validation.validation_results.is_valid
                    messages = []
                    
                    if hasattr(validation.validation_results, 'messages'):
                        messages = [msg.text for msg in validation.validation_results.messages]
                    
                    return {
                        'is_valid': is_valid,
                        'messages': messages
                    }
                
                # If no validation results, assume valid
                logger.warning("No validation results received, assuming address is valid")
                return {
                    'is_valid': True,
                    'messages': ['Address accepted without validation']
                }
                
            except Exception as e:
                logger.warning(f"Address validation failed, but proceeding: {str(e)}")
                return {
                    'is_valid': True,
                    'messages': ['Address accepted despite validation error']
                }
            
        except Exception as e:
            logger.error(f"Address validation error: {str(e)}", exc_info=True)
            return {
                'is_valid': False,
                'messages': [str(e)]
            }

class SellerAddress(Address):
    """Seller's pickup/warehouse addresses - extends base Address model"""
    seller = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='addresses')  # Link to seller user
    is_warehouse = models.BooleanField(default=False)  # Whether this is a warehouse address
    warehouse_hours = models.JSONField(null=True, blank=True, help_text="Operating hours for pickup")  # Store hours as JSON

    class Meta:
        unique_together = [['seller', 'is_default']]  # Ensure only one default address per seller
        verbose_name = "Seller Address"
        verbose_name_plural = "Seller Addresses"

    def clean(self):
        """Ensure only one default address per seller"""
        if self.is_default:
            # Set all other addresses for this seller to non-default
            SellerAddress.objects.filter(seller=self.seller, is_default=True).exclude(id=self.id).update(is_default=False)

class BuyerAddress(Address):
    """Buyer's delivery addresses - extends base Address model"""
    buyer = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='delivery_addresses')  # Link to buyer user
    is_residential = models.BooleanField(default=True)  # Whether this is a residential address
    delivery_instructions = models.TextField(blank=True, null=True)  # Special delivery instructions

    class Meta:
        unique_together = [['buyer', 'is_default']]  # Ensure only one default address per buyer
        verbose_name = "Buyer Address"
        verbose_name_plural = "Buyer Addresses"

    def clean(self):
        """Ensure only one default address per buyer"""
        if self.is_default:
            # Set all other addresses for this buyer to non-default
            BuyerAddress.objects.filter(buyer=self.buyer, is_default=True).exclude(id=self.id).update(is_default=False)

class Shipping(models.Model):
    """Shipping Model with Shippo Integration - handles all shipping related data"""
    SHIPPING_STATUS = (  # Status choices for shipment tracking
        ('PENDING', 'Pending'),
        ('TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('RETURNED', 'Returned'),
        ('FAILURE', 'Delivery Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)  # Unique identifier for shipment
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='shipping')  # Link to order
    from_address = models.ForeignKey(SellerAddress, on_delete=models.PROTECT, related_name='shipments_from')  # Sender address
    to_address = models.ForeignKey(BuyerAddress, on_delete=models.PROTECT, related_name='shipments_to')  # Recipient address
    
    # Shippo specific fields for tracking and labels
    shippo_transaction_id = models.CharField(max_length=255, blank=True, null=True)  # Shippo transaction reference
    shippo_rate_id = models.CharField(max_length=255, blank=True, null=True)  # Selected shipping rate reference
    tracking_number = models.CharField(max_length=100, blank=True, null=True)  # Carrier tracking number
    tracking_url = models.URLField(blank=True, null=True)  # URL for tracking shipment
    label_url = models.URLField(blank=True, null=True)  # URL for shipping label
    
    carrier = models.CharField(max_length=100)  # Shipping carrier name
    shipping_method = models.CharField(max_length=100)  # Shipping service level
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Cost of shipping
    estimated_delivery_date = models.DateField(null=True, blank=True)  # Expected delivery date
    
    status = models.CharField(max_length=20, choices=SHIPPING_STATUS, default='PENDING')  # Current shipping status
    created_at = models.DateTimeField(auto_now_add=True)  # When shipment was created
    updated_at = models.DateTimeField(auto_now=True)  # When shipment was last updated
    shipped_at = models.DateTimeField(null=True, blank=True)  # When shipment was sent
    delivered_at = models.DateTimeField(null=True, blank=True)  # When shipment was delivered

    def create_shippo_label(self, rate_id=None):
        """Create shipping label using Shippo SDK
        Args:
            rate_id: Optional specific rate to use for label
        Returns:
            Tuple of (success boolean, transaction object or None, error_message)"""
        try:
            # Verify Shippo API key
            if not settings.SHIPPO_API_KEY:
                error_msg = "Shippo API key not configured"
                logger.error(error_msg)
                return False, None, error_msg
                
            logger.info(f"Using Shippo API key: {settings.SHIPPO_API_KEY[:6]}...")
            
            logger.info(f"Starting create_shippo_label with rate_id: {rate_id}")
            order = self.order
            product = order.product

            # Verify order is paid
            if not hasattr(order, 'payment') or order.payment.payment_status != 'completed':
                error_msg = "Cannot create label for unpaid order"
                logger.error(error_msg)
                return False, None, error_msg

            # Validate product dimensions
            logger.info(f"Product dimensions - L:{product.length}, W:{product.width}, H:{product.height}, Weight:{product.weight}")
            if not all([product.length, product.width, product.height, product.weight]):
                error_msg = "Missing product dimensions"
                logger.error(error_msg)
                return False, None, error_msg

            try:
                # Create sender address in Shippo
                logger.info("Creating sender address...")
                from_address_data = self.from_address.to_shippo_dict()
                logger.info(f"From address data: {from_address_data}")
                from_address = shippo_sdk.addresses.create(from_address_data)
                logger.info(f"From address created: {from_address.object_id}")
                
                # Validate sender address
                logger.info("Validating sender address...")
                validation = shippo_sdk.addresses.validate(from_address.object_id)
                logger.info(f"Validation response: {validation}")
                
                if not validation.validation_results.is_valid:
                    messages = [msg.text for msg in validation.validation_results.messages] if hasattr(validation.validation_results, 'messages') else ['Address validation failed']
                    error_msg = f"Sender address validation failed: {messages}"
                    logger.error(error_msg)
                    return False, None, error_msg
                
                logger.info("Sender address validated successfully")
            except Exception as e:
                error_msg = f"Failed to create/validate sender address: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg

            try:
                # Create recipient address in Shippo
                logger.info("Creating recipient address...")
                to_address_data = self.to_address.to_shippo_dict()
                logger.info(f"To address data: {to_address_data}")
                to_address = shippo_sdk.addresses.create(to_address_data)
                logger.info(f"To address created: {to_address.object_id}")
                
                # Skip validation for residential addresses
                if hasattr(self.to_address, 'is_residential') and self.to_address.is_residential:
                    logger.info("Skipping validation for residential address")
                else:
                    # Validate recipient address
                    logger.info("Validating recipient address...")
                    validation = shippo_sdk.addresses.validate(to_address.object_id)
                    logger.info(f"Validation response: {validation}")
                    
                    if not validation.validation_results.is_valid:
                        messages = [msg.text for msg in validation.validation_results.messages] if hasattr(validation.validation_results, 'messages') else ['Address validation failed']
                        error_msg = f"Recipient address validation failed: {messages}"
                        logger.error(error_msg)
                        return False, None, error_msg
                
                logger.info("Recipient address processing completed")
            except Exception as e:
                error_msg = f"Failed to create/validate recipient address: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg

            try:
                # Create parcel object in Shippo
                logger.info("Creating parcel...")
                parcel_data = components.ParcelCreateRequest(
                    length=str(float(product.length)),
                    width=str(float(product.width)),
                    height=str(float(product.height)),
                    distance_unit="in",
                    weight=str(float(product.weight)),
                    mass_unit="lb"
                )
                logger.info(f"Parcel data: {parcel_data}")
                parcel = shippo_sdk.parcels.create(parcel_data)
                logger.info(f"Parcel created: {parcel.object_id}")
            except Exception as e:
                error_msg = f"Failed to create parcel: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg

            try:
                # Create shipment in Shippo
                logger.info("Creating shipment...")
                shipment_data = components.ShipmentCreateRequest(
                    address_from=from_address.object_id,
                    address_to=to_address.object_id,
                    parcels=[parcel.object_id],
                    async_=False
                )
                logger.info(f"Shipment data: {shipment_data}")
                shipment = shippo_sdk.shipments.create(shipment_data)
                logger.info(f"Shipment created: {shipment.object_id}")

                # Validate and log available rates
                if not hasattr(shipment, 'rates') or not shipment.rates:
                    error_msg = "No shipping rates available for this shipment"
                    logger.error(error_msg)
                    return False, None, error_msg

                logger.info(f"Available rates: {[f'{rate.provider} - {rate.servicelevel.name} - ${rate.amount}' for rate in shipment.rates]}")
            except Exception as e:
                error_msg = f"Failed to create shipment: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg

            # Validate rate_id
            if not rate_id and hasattr(shipment, 'rates') and shipment.rates:
                # Find the cheapest rate from a major carrier
                preferred_carriers = ['USPS', 'UPS', 'FEDEX']
                available_rates = [rate for rate in shipment.rates if rate.provider in preferred_carriers]
                if available_rates:
                    rate_id = min(available_rates, key=lambda x: float(x.amount)).object_id
                else:
                    rate_id = shipment.rates[0].object_id
                logger.info(f"Selected rate_id: {rate_id}")
            elif not rate_id:
                error_msg = "No rates available for shipment"
                logger.error(error_msg)
                return False, None, error_msg

            try:
                # Purchase shipping label
                logger.info(f"Creating transaction with rate_id: {rate_id}")
                transaction_data = components.TransactionCreateRequest(
                    rate=rate_id,
                    async_=False,
                    label_file_type="PDF"
                )
                transaction = shippo_sdk.transactions.create(transaction_data)
                logger.info(f"Transaction created with status: {transaction.status}")
                
                # Log detailed transaction information
                logger.info(f"Transaction details: ID={transaction.object_id}, "
                          f"Status={transaction.status}, "
                          f"Label URL={getattr(transaction, 'label_url', 'N/A')}, "
                          f"Tracking Number={getattr(transaction, 'tracking_number', 'N/A')}")

                if hasattr(transaction, 'messages'):
                    logger.error(f"Transaction messages: {transaction.messages}")
            except Exception as e:
                error_msg = f"Failed to create transaction: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg

            # Check transaction status
            if transaction.status == "SUCCESS":
                logger.info("Transaction successful, updating shipping record...")
                try:
                    # Update shipping record
                    self.shippo_transaction_id = transaction.object_id
                    self.tracking_number = transaction.tracking_number
                    self.tracking_url = transaction.tracking_url_provider
                    self.label_url = transaction.label_url
                    self.carrier = transaction.rate.provider
                    self.shipping_method = transaction.rate.servicelevel.name
                    self.shipping_cost = transaction.rate.amount
                    self.save()

                    # Update order total to include actual shipping cost
                    order.total_price = order.product.price * order.quantity + self.shipping_cost
                    order.save()

                    # Create shipping status history
                    ShippingStatusHistory.objects.create(
                        shipping=self,
                        status='PENDING',
                        description='Shipping label created successfully'
                    )

                    return True, transaction, None
                except Exception as e:
                    error_msg = f"Failed to update shipping record: {str(e)}"
                    logger.error(error_msg)
                    return False, transaction, error_msg
            else:
                error_msg = f"Transaction failed with status: {transaction.status}"
                if hasattr(transaction, 'messages'):
                    error_msg += f" - Messages: {transaction.messages}"
                logger.error(error_msg)
                return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error in create_shippo_label: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg

    def get_shipping_rates(self):
        """Get available shipping rates using Shippo SDK
        Returns list of available shipping rates"""
        try:
            logger.info("Starting shipping rate calculation...")
            order = self.order
            product = order.product

            # Validate product dimensions
            logger.info(f"Product dimensions - L:{product.length}, W:{product.width}, H:{product.height}, Weight:{product.weight}")
            if not all([product.length, product.width, product.height, product.weight]):
                logger.error("Missing product dimensions")
                return []

            try:
                # Create sender address in Shippo
                logger.info("Creating sender address...")
                from_address_data = self.from_address.to_shippo_dict()
                logger.info(f"From address data: {from_address_data}")
                from_address = shippo_sdk.addresses.create(from_address_data)
                logger.info(f"From address created: {from_address.object_id}")
                
                # Validate sender address
                logger.info("Validating sender address...")
                validation = shippo_sdk.addresses.validate(from_address.object_id)
                logger.info(f"Validation response: {validation}")
                
                if not validation.validation_results.is_valid:
                    messages = [msg.text for msg in validation.validation_results.messages] if hasattr(validation.validation_results, 'messages') else ['Address validation failed']
                    logger.error(f"Sender address validation failed: {messages}")
                    return []
                
                logger.info("Sender address validated successfully")
            except Exception as e:
                logger.error(f"Failed to create/validate sender address: {str(e)}")
                return []

            try:
                # Create recipient address in Shippo
                logger.info("Creating recipient address...")
                to_address_data = self.to_address.to_shippo_dict()
                logger.info(f"To address data: {to_address_data}")
                to_address = shippo_sdk.addresses.create(to_address_data)
                logger.info(f"To address created: {to_address.object_id}")
                
                # Validate recipient address
                logger.info("Validating recipient address...")
                validation = shippo_sdk.addresses.validate(to_address.object_id)
                logger.info(f"Validation response: {validation}")
                
                if not validation.validation_results.is_valid:
                    messages = [msg.text for msg in validation.validation_results.messages] if hasattr(validation.validation_results, 'messages') else ['Address validation failed']
                    logger.error(f"Recipient address validation failed: {messages}")
                    return []
                
                logger.info("Recipient address validated successfully")
            except Exception as e:
                logger.error(f"Failed to create/validate recipient address: {str(e)}")
                return []

            try:
                # Create parcel in Shippo
                logger.info("Creating parcel...")
                parcel_data = components.ParcelCreateRequest(
                    length=str(product.length),
                    width=str(product.width),
                    height=str(product.height),
                    distance_unit="in",
                    weight=str(product.weight),
                    mass_unit="lb"
                )
                logger.info(f"Parcel data: {parcel_data}")
                parcel = shippo_sdk.parcels.create(parcel_data)
                logger.info(f"Parcel created: {parcel.object_id}")
            except Exception as e:
                logger.error(f"Failed to create parcel: {str(e)}")
                return []

            try:
                # Create shipment to get rates
                logger.info("Creating shipment...")
                shipment_data = components.ShipmentCreateRequest(
                    address_from=from_address.object_id,
                    address_to=to_address.object_id,
                    parcels=[parcel.object_id],
                    async_=False
                )
                logger.info(f"Shipment data: {shipment_data}")
                shipment = shippo_sdk.shipments.create(shipment_data)
                logger.info(f"Shipment created: {shipment.object_id}")

                # Wait for rates to be available
                if hasattr(shipment, 'rates') and shipment.rates:
                    logger.info(f"Found {len(shipment.rates)} rates")
                    # Log available rates for debugging
                    for rate in shipment.rates:
                        logger.info(f"Rate: {rate.provider} - {rate.servicelevel.name} - ${rate.amount}")
                    return shipment.rates
                else:
                    logger.warning("No rates available for shipment")
                    return []

            except Exception as e:
                logger.error(f"Failed to create shipment: {str(e)}")
                return []

        except Exception as e:
            logger.error(f"Error getting shipping rates: {str(e)}", exc_info=True)
            return []

class ShippingStatusHistory(models.Model):
    """Track shipping status changes over time"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)  # Unique identifier
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='status_history')  # Link to shipping record
    status = models.CharField(max_length=20)  # Status at this point
    location = models.CharField(max_length=255, null=True, blank=True)  # Location at this status
    description = models.TextField(null=True, blank=True)  # Additional status details
    created_at = models.DateTimeField(auto_now_add=True)  # When status was recorded

    class Meta:
        ordering = ['-created_at']  # Order by most recent first
        verbose_name = "Shipping Status History"
        verbose_name_plural = "Shipping Status Histories"

@receiver(pre_save, sender=SellerAddress)
@receiver(pre_save, sender=BuyerAddress)
def validate_address_on_save(sender, instance, **kwargs):
    """Validate address using Shippo before saving to database
    Raises ValidationError if address is invalid"""
    if not instance.is_verified:
        validation_results = instance.validate_address()
        if validation_results and not validation_results['is_valid']:
            raise ValidationError({
                'address': validation_results['messages']
            })
