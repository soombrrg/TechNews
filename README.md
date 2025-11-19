# News Project

A modern, full-featured news platform built with Django REST Framework, featuring subscription management, payment processing, and real-time content delivery.

## 🚀 Features

- **User Management**: Custom user authentication with JWT tokens
- **News Articles**: Full CRUD operations for news content
- **Comments System**: Nested comments with moderation capabilities
- **Subscription Management**: Tiered subscription plans with automated expiry handling
- **Payment Integration**: Stripe payment processing with webhook support
- **Media Storage**: S3-compatible storage (MinIO) for static and media files
- **Async Tasks**: Celery-based background job processing
- **API Documentation**: Interactive Swagger/ReDoc documentation
- **Caching**: Redis-based caching with Django-Cachalot ORM cache
- **Admin Panel**: Enhanced Django admin with import/export functionality

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.16+
- **Database**: PostgreSQL 17
- **Cache**: Redis 6.4+
- **Task Queue**: Celery 5.5+ with Redis broker
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Payment**: Stripe API
- **Storage**: S3-compatible (MinIO/AWS S3)
- **Server**: Uvicorn ASGI server

### DevOps
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Task Monitoring**: Flower (Celery monitoring)
- **Package Manager**: uv

### Development Tools
- **Testing**: pytest, pytest-django, pytest-cov, schemathesis
- **Code Quality**: black, isort, flake8, mypy
- **Pre-commit Hooks**: pre-commit
- **Type Checking**: mypy with django-stubs

## 📋 Prerequisites

- Python 3.12+
- Docker & Docker Compose
- uv package manager
- PostgreSQL 17 (for local development)
- Redis (for local development)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd news_project
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example src/.env
```

Edit `src/.env` with your configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,web

# Database
DATABASE_URL=postgres://postgres@localhost:5432/postgres

# Redis
REDIS_URL=redis://@localhost:6379/1

# Stripe (get from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# S3 Storage
USE_S3=True
AWS_ACCESS_KEY_ID=user
AWS_SECRET_ACCESS_KEY=password
AWS_S3_ENDPOINT_URL=http://localhost:9000
AWS_STORAGE_BUCKET_NAME=local-static

# Celery
USE_CELERY=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Install Dependencies

```bash
make deps
# or
uv sync
```

### 4. Run with Docker (Recommended)

```bash
# Build the Docker image
make build

# Start all services
docker-compose up -d
```

Services will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Flower (Celery Monitor)**: http://localhost:5555 (admin:admin)
- **MinIO Console**: http://localhost/s3/ui (user:password)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 5. Local Development Setup

```bash
# Run migrations
make prep

# Start development server
make up

# In separate terminals:
# Run Celery worker
make worker

# Run Celery beat (for scheduled tasks)
celery -A app --workdir src beat --loglevel=info
```

## 📁 Project Structure

```
news_project/
├── src/
│   ├── accounts/          # User management & authentication
│   ├── app/              # Main Django configuration
│   ├── comments/         # Comments system
│   ├── main/             # News articles & core functionality
│   ├── payments/         # Stripe payment integration
│   ├── subscribe/        # Subscription management
│   ├── static/           # Static files
│   ├── manage.py         # Django management script
│   └── conftest.py       # Pytest configuration
├── nginx/                # Nginx configuration
├── postgres/             # PostgreSQL data
├── minio/                # MinIO S3 storage
├── .env.example          # Environment variables template
├── compose.yaml          # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── Makefile              # Development commands
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## 🧪 Testing

The project follows a test-driven development approach.

```bash
# Run all tests
make test

# Run tests with coverage
cd src && uv run pytest --cov

# Run specific test file
cd src && uv run pytest accounts/tests/test_models.py

# Run with verbose output
cd src && uv run pytest -v

# Run API schema tests
uv run pytest test_schemathesis.py
```

## 🎨 Code Quality

```bash
# Format code
make fmt

# Run linters
make lint

# Run all checks
make fmt lint test
```

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

### API Versioning

The API uses URL path versioning:
- Current version: `/api/v1/`

### Authentication

The API uses JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-access-token>
```

### Example Endpoints

```bash
# User Registration
POST /api/v1/accounts/register/

# Login
POST /api/v1/accounts/login/

# Get News Articles
GET /api/v1/news/

# Create Comment
POST /api/v1/comments/

# Subscribe
POST /api/v1/subscriptions/

# Create Payment
POST /api/v1/payments/create-checkout-session/
```

## 🔄 Celery Tasks

The project includes several automated background tasks:

- **Subscription Management**:
  - Check expired subscriptions (every hour)
  - Send expiry reminders (daily)
  
- **Payment Processing**:
  - Cleanup old payments (weekly)
  - Cleanup old webhook events (daily)
  - Retry failed webhook events (hourly)

Monitor tasks in Flower: http://localhost:5555

## 🗄️ Database Migrations

```bash
# Create migrations
uv run python src/manage.py makemigrations

# Apply migrations
uv run python src/manage.py migrate

# Or use Makefile
make prep
```

## 🔐 Security

- JWT token authentication with refresh token rotation
- CSRF protection enabled
- Secure cookie settings in production
- Rate limiting for anonymous users (100 requests/hour)
- SQL injection protection via Django ORM
- XSS protection headers

### Production Security Checklist

Set `SECURITY_MODE=prod` in `.env` to enable:
- SSL redirect
- Secure cookies
- XSS filter
- Content type nosniff
- X-Frame-Options: DENY

## 🚀 Deployment

### Production Build

```bash
# Build production image
docker build -t news-project:latest .

# Run production server
make up-prod
```

### Environment Variables for Production

```env
DEBUG=False
SECURITY_MODE=prod
MAILING_MODE=prod
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgres://user:password@host:5432/dbname
```

## 📊 Monitoring

- **Celery Tasks**: Flower at http://localhost:5555
- **Database**: PostgreSQL logs
- **Application Logs**: Configure `LOGGING_MODE=prod` for file-based logging
- **API Performance**: Django Debug Toolbar (development only)

## 🤝 Contributing

1. Write tests first (TDD approach)
2. Follow code style (black + isort)
3. Run linters before committing
4. Update documentation as needed

## 📝 Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Write tests
cd src && uv run pytest

# 3. Implement feature
# ... code ...

# 4. Format and lint
make fmt lint

# 5. Run tests
make test

# 6. Commit changes
git commit -m "feat: your feature description"
```

## 🔗 Related Projects

- **Frontend**: news_project_front

## 📄 License

[Add your license here]

## 👥 Authors

[Add author information here]

## 🐛 Known Issues

- Check the issue tracker for current known issues

## 📞 Support

For support, please [add contact information or issue tracker link]