import shippo
from shippo.models import components

shippo_sdk = shippo.Shippo(api_key_header="shippo_test_be3230c139d1239312533a6aae6468a404e077c2")

# Create sender address
from_address = shippo_sdk.addresses.create(
    components.AddressCreateRequest(
        name="Shawn Ippotle",
        company="Shippo",
        street1="215 Clayton St.", 
        city="San Francisco",
        state="CA",
        zip="94117",
        country="US",
        phone="+1 555 341 9393",
        email="shippotle@shippo.com"
    )
)

# Create recipient address
to_address = shippo_sdk.addresses.create(
    components.AddressCreateRequest(
        name="Mr Hippo",
        company="Shippo", 
        street1="123 Main Street",
        city="Los Angeles",
        state="CA",
        zip="90012",
        country="US",
        phone="+1 555 341 9393",
        email="mrhippo@goshippo.com"
    )
)

# Create parcel
parcel = shippo_sdk.parcels.create(
    components.ParcelCreateRequest(
        length="5",
        width="5", 
        height="5",
        distance_unit="in",
        weight="2",
        mass_unit="lb"
    )
)

# Create shipment
shipment = shippo_sdk.shipments.create(
    components.ShipmentCreateRequest(
        address_from=from_address.object_id,
        address_to=to_address.object_id,
        parcels=[parcel.object_id],
        async_=False
    )
)

# Get and display shipping rates in a more readable format
print("\nAvailable Shipping Rates:")
print("-" * 50)
for rate in shipment.rates:
    print(f"Carrier: {rate.provider}")
    print(f"Service: {rate.servicelevel.name}")
    print(f"Amount: ${rate.amount}")
    print(f"Estimated Days: {rate.estimated_days}")
    print(f"Rate ID: {rate.object_id}")
    print("-" * 50)

# Purchase label with first rate
try:
    # Filter for UPS rates
    ups_rates = [rate for rate in shipment.rates if rate.provider == "UPS"]
    
    if not ups_rates:
        print("\nNo UPS rates available. Please try another carrier.")
    else:
        # Use first UPS rate
        transaction = shippo_sdk.transactions.create(
            components.TransactionCreateRequest(
                rate=ups_rates[0].object_id,
                async_=False
            )
        )
        
        # Check if transaction was successful
        if transaction.status == "SUCCESS":
            print("\nShipping Label Details:")
            print("-" * 50)
            print("Shipping label URL:", transaction.label_url)
            print("Tracking number:", transaction.tracking_number)
        else:
            print("\nError creating shipping label:")
            print("-" * 50)
            print("Status:", transaction.status)
            print("Message:", transaction.messages)
            print("\nPlease register your UPS account at https://apps.goshippo.com/settings/carriers")
            
except Exception as e:
    print("\nError creating shipping label:")
    print("-" * 50) 
    print("Exception:", str(e))