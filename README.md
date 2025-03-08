# AuraSpot Marketplace

## About The Project

AuraSpot is a comprehensive e-commerce marketplace platform that connects buyers and sellers, facilitating secure transactions and efficient shipping services. The platform is built with a Django REST Framework backend and provides a robust API for seamless integration with various frontend applications.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Admin, Buyer, Seller)
  - Email verification system

- **Product Management**
  - Product listing and categorization
  - Product search and filtering
  - Image upload and management
  - Inventory tracking

- **Order Management**
  - Shopping cart functionality
  - Order processing and tracking
  - Order history

- **Shipping Integration**
  - Shippo API integration
  - Shipping rate calculation
  - Label generation
  - Tracking updates

- **User Management**
  - Buyer profiles
  - Seller profiles and stores
  - User analytics

- **Payment Processing**
  - Secure payment integration
  - Transaction history
  - Refund management

## Project Structure

```
auraspotmarketplace1/
├── apps/
│   ├── analytics/      # User and business analytics
│   ├── authentication/ # User authentication and authorization
│   ├── buyers/         # Buyer-specific functionality
│   ├── orders/         # Order processing and management
│   ├── payments/       # Payment processing
│   ├── products/       # Product management
│   ├── rewards/        # Customer loyalty program
│   ├── sellers/        # Seller management
│   └── shipping/       # Shipping integration with Shippo
├── media/              # User-uploaded files
├── nginx/              # Nginx configuration
└── auraspotmarketplace1/  # Core project settings
```

## API Endpoints

- **Authentication** (`/auth/`)
  - Registration
  - Login
  - Password reset
  - Email verification

- **Products** (`/products/`)
  - List/Create products
  - Product details
  - Category management

- **Orders** (`/orders/`)
  - Create/View orders
  - Order status updates
  - Order history

- **Shipping** (`/shipping/`)
  - Rate calculation
  - Label generation
  - Tracking information

- **Sellers** (`/sellers/`)
  - Store management
  - Sales analytics
  - Inventory management

- **Buyers** (`/buyers/`)
  - Profile management
  - Purchase history
  - Wishlist

## Tech Stack

### Backend
- **Framework**: Django 5.1.6
- **API**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.1)
- **Database**: PostgreSQL (with Neon.tech)
- **File Storage**: Local storage with Pillow support
- **Email**: SMTP with Gmail
- **Shipping**: Shippo API
- **Other Tools**:
  - django-cors-headers
  - django-filter
  - python-dotenv
  - whitenoise
  - gunicorn

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (or Neon.tech account)
- Shippo API key
- SMTP server access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdiesu04/nexus.git
   cd nexus
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Update .env with your configuration
   ```

3. **Backend Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

### Docker Setup
```bash
docker-compose up --build
```

## Documentation

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Shipping Integration**: See `SHIPPING_DOCUMENTATION.md`

## Development

The application uses a modular architecture with:
- Separate apps for different functionalities
- RESTful API design
- Comprehensive test coverage
- Docker support for development and deployment

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Abdi - [@abdiesu04](https://github.com/abdiesu04)

Project Link: [https://github.com/abdiesu04/nexus](https://github.com/abdiesu04/nexus)