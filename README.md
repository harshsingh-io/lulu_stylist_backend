# AI Stylist App Backend

[![wakatime](https://wakatime.com/badge/user/018ecd32-5efb-491a-be09-136c9f428be6/project/713d784e-7e8e-4a1a-9c14-5b8ea0dcbb5f.svg)](https://wakatime.com/badge/user/018ecd32-5efb-491a-be09-136c9f428be6/project/713d784e-7e8e-4a1a-9c14-5b8ea0dcbb5f)

A robust and scalable FastAPI backend for the AI Stylist App that provides personalized fashion advice through an AI chat interface, wardrobe management, and user profile customization.

[Front-End Of Lulu AI Fashion Stylist](https://github.com/harshsingh-io/lulu_stylist_app)

[Docs](http://54.197.163.177:8000/docs)

## Features

- 🤖 ********AI Chat Interface********: Personalized outfit suggestions and fashion tips using OpenAI integration
- 👕 ********Wardrobe Management********: Digital wardrobe organization with image upload and categorization
- 👤 ********User Profile Management********: Detailed user preferences and measurements storage
- 🔐 ********JWT Authentication********: Secure access with refresh token support
- 📦 ********Microservices Architecture********: Scalable design with separate services
- ☁️ ********Cloud Storage********: AWS S3 integration for image storage
- 📊 ********Dual Database********: PostgreSQL for structured data, MongoDB for chat history

## Technology Stack

- ********Backend Framework********: FastAPI
- ********Databases********:
  - PostgreSQL (User data, Wardrobe items)
  - MongoDB (Chat sessions, Messages)
- ********Cloud Services********:
  - AWS S3 (Image storage)
  - OpenAI API (Chat intelligence)
- ********Development Tools********:
  - Docker & Docker Compose
  - Alembic (Database migrations)
  - GitHub Actions (CI/CD)

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL
- MongoDB
- AWS Account (for S3)
- OpenAI API Key

## Installation

1. ********Clone the Repository********:
```bash
git clone https://github.com/yourusername/ai-stylist-backend.git
cd ai-stylist-backend
```

2. ********Environment Setup********:
   Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/ai_fashion_app
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=ai_fashion_app

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ai_chat
MONGODB_HOST=mongodb

# JWT Configuration
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_SECRET_KEY=<your-refresh-secret-key>

# AWS Configuration
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_REGION=us-east-1
AWS_S3_BUCKET=aifashion-images

# OpenAI Configuration
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MAX_TOKENS=8000
```

3. ********Docker Deployment********:
```bash
_# Build and start services_
docker compose up -d

_# Check logs_
docker compose logs -f
```

4. ********Local Development Setup********:
```bash
_# Create virtual environment_
python -m venv venv
source venv/bin/activate  _# On Windows: venv\Scripts\activate_

_# Install dependencies_
pip install -r requirements.txt

_# Run migrations_
alembic upgrade head

_# Start the application_
uvicorn app.main:app --reload
```

## Project Structure
```
├── app/
│   ├── auth/ # Authentication & authorization
│   ├── database/ # Database connections & models
│   ├── models/ # SQLAlchemy models
│   ├── routers/ # API routes
│   ├── schemas/ # Pydantic models
│   ├── services/ # Business logic
│   └── main.py # Application entry point
├── migrations/         # Alembic migrations
├── tests/             # Test files
├── docs/              # Documentation
├── .github/           # GitHub Actions workflows
├── docker-compose.yml # Docker composition
├── requirements.txt   # Python dependencies
└── README.md
```

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/refresh` - Refresh access token

#### User Management
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me/profile` - Update user profile
- `POST /api/users/me/profile-picture` - Upload profile picture

#### Wardrobe
- `GET /api/wardrobe/items` - List wardrobe items
- `POST /api/wardrobe/items` - Add new item
- `GET /api/wardrobe/items/{item_id}` - Get item details
- `PUT /api/wardrobe/items/{item_id}` - Update item
- `DELETE /api/wardrobe/items/{item_id}` - Delete item
- `POST /api/wardrobe/items/{item_id}/image` - Upload item image

#### Chat
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - List chat sessions
- `POST /api/chat/{session_id}/message` - Send message
- `GET /api/chat/{session_id}` - Get chat history

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
_# Create a new migration_
alembic revision --autogenerate -m "description"

_# Apply migrations_
alembic upgrade head
```

## Deployment

The application uses GitHub Actions for CI/CD. On push to main:
1. Tests are run
2. Docker images are built
3. Application is deployed to production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


