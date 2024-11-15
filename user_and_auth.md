# User Management API with FastAPI

A robust FastAPI backend application implementing user management system with JWT authentication.

## Features

- 🔐 JWT Authentication
- 👤 User Management (CRUD Operations)
- 🛢️ PostgreSQL Database with SQLAlchemy ORM
- 📝 OpenAPI Documentation (Swagger UI)
- 🔒 Secure Password Hashing
- ⚡ Fast and Async

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Python-Jose (JWT)
- Passlib
- Uvicorn
- Python 3.8+

## Project Structure

```
📦user_management
 ┣ 📂app
 ┃ ┣ 📂auth
 ┃ ┃ ┣ 📜jwt_handler.py
 ┃ ┃ ┗ 📜jwt_bearer.py
 ┃ ┣ 📂crud
 ┃ ┃ ┗ 📜user.py
 ┃ ┣ 📂database
 ┃ ┃ ┣ 📜base.py
 ┃ ┃ ┗ 📜session.py
 ┃ ┣ 📂models
 ┃ ┃ ┗ 📜user.py
 ┃ ┣ 📂schemas
 ┃ ┃ ┗ 📜user.py
 ┃ ┣ 📂routes
 ┃ ┃ ┗ 📜user.py
 ┃ ┗ 📜main.py
 ┣ 📜.env
 ┣ 📜.gitignore
 ┣ 📜requirements.txt
 ┗ 📜README.md
```

## Prerequisites

- Python 3.8+
- PostgreSQL
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd user_management
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Ensure PostgreSQL is installed and running on your system.

```sql
-- Connect to PostgreSQL and create database
CREATE DATABASE user_management_db;
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory (it's already in .gitignore):

```env
DATABASE_URL=postgresql://hanu:helloworld@localhost:5432/user_management_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Make sure to replace the database credentials and secret key with your own values.

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

After running the application, you can access:
- Swagger UI Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register` | Register new user | No |
| POST | `/api/login` | Login user | No |
| GET | `/api/users` | List all users | Yes |
| GET | `/api/users/me` | Get current user | Yes |
| PUT | `/api/users/{user_id}` | Update user | Yes |
| DELETE | `/api/users/{user_id}` | Delete user | Yes |

## Development

### Code Style

This project follows PEP 8 guidelines. To maintain code quality:

1. Install development dependencies:
```bash
pip install black flake8 isort
```

2. Format code:
```bash
black .
isort .
flake8
```

### Git Workflow

1. Create a new branch for each feature/bugfix
2. Follow conventional commits for commit messages
3. Create PR for review
4. Merge after approval

### Testing

```bash
# Install pytest
pip install pytest

# Run tests
pytest
```

## Deployment

For production deployment:

1. Update `.env` with production settings
2. Use proper WSGI server (e.g., Gunicorn)
3. Set up proper security measures
4. Use proper database credentials
5. Set up proper logging

Example production run:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- FastAPI Documentation
- SQLAlchemy Documentation
- JWT Authentication Best Practices
