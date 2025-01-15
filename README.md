# AI Stylist App Backend .

The backend for the AI Stylist App provides a robust and scalable infrastructure to deliver personalized fashion advice through an interactive AI chat interface. It allows users to manage their wardrobe digitally and enhances recommendations based on individual user details.

[Front-End Of Lulu AI Fashion Stylist](https://github.com/harshsingh-io/lulu_stylist_app)

[Docs](http://54.197.163.177:8000/docs)

## Features

- **AI Chat Interface**: Engage with an AI stylist for personalized outfit suggestions and fashion tips.
- **Wardrobe Management**: Upload, categorize, and manage your clothing items to receive tailored recommendations.
- **User Profile Management**: Store and update personal details to refine the AI's styling advice.
- **Authentication and Authorization**: Secure user data with JWT-based authentication.
- **Scalable Architecture**: Designed using microservices for efficient scaling and maintenance.

## Technology Stack

- **Programming Language**: Python
- **Framework**: FastAPI for building APIs
- **Databases**:
    - **Relational**: PostgreSQL for structured data
    - **NoSQL**: MongoDB for flexible document storage
- **AI Integration**:
    - Natural Language Processing with integrated AI models
    - Image Recognition using machine learning libraries
- **Containerization**: Docker for consistent deployment
- **Cloud Services**: Hosted on cloud platforms with container orchestration

## Installation

1. **Clone the Repository**:

     ```bash
     git clone https://github.com/yourusername/ai-stylist-backend.git
     cd ai-stylist-backend
     ```

2. **Create a Virtual Environment**:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:

     ```bash
     pip install -r requirements.txt
     ```

4. **Set Up Environment Variables**:

     - Create a `.env` file and add the necessary configurations (database credentials, secret keys, etc.).
        ```env
        DATABASE_URL=postgresql://<username>:<password>@localhost:5432/ai_fashion_app
        SECRET_KEY=<generated-jwt-key>
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=1000

        # AWS S3 Configuration
        AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
        AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
        AWS_REGION=us-east-1
        AWS_S3_BUCKET=aifashion-images

        # MongoDB Configuration
        MONGODB_URL=mongodb://localhost:27017
        MONGODB_DB_NAME=ai_chat

        # OpenAI Configuration
        OPENAI_API_KEY=<your-openai-api-key>
        OPENAI_MODEL=gpt-4
        OPENAI_MAX_TOKENS=8000
        ```

5. **Run Database Migrations**:

     ```bash
     alembic upgrade head
     ```

6. **Start the Application**:

     ```bash
     uvicorn app.main:app --reload
     ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` for interactive exploration.
- Use API clients like Postman to test endpoints.
- Integrate the backend with the frontend application to enable full functionality.

## Project Structure

```
├── app
│   ├── auth
│   ├── database
│   ├── models
│   ├── routers
│   ├── schemas
│   ├── services
│   └── main.py
├── tests
├── migrations
├── requirements.txt
└── README.md
```
## Usage


1. [Users](#users)
2. [Wardrobe](#wardrobe)
3. [Chat](#chat)

---

## Users

Endpoints for user registration, authentication, and profile management.

- **POST** `/api/register`  
  Register a new user account.

- **POST** `/api/login`  
  Authenticate a user and provide an access token.

- **GET** `/api/users/me`  
  Retrieve the authenticated user's information.

- **PUT** `/api/users/me/profile`  
  Update the authenticated user's profile information.

- **POST** `/api/users/me/profile-picture`  
  Upload or update the user's profile picture.

- **DELETE** `/api/users/me/profile-picture`  
  Remove the user's profile picture.

---

## Wardrobe

Endpoints for managing wardrobe items.

- **GET** `/api/wardrobe/items`  
  Retrieve a list of wardrobe items.

- **POST** `/api/wardrobe/items`  
  Add a new item to the user's wardrobe.

- **GET** `/api/wardrobe/items/{item_id}`  
  Retrieve details of a specific wardrobe item.

- **PUT** `/api/wardrobe/items/{item_id}`  
  Update information of a specific wardrobe item.

- **DELETE** `/api/wardrobe/items/{item_id}`  
  Remove a specific item from the user's wardrobe.

- **POST** `/api/wardrobe/items/{item_id}/image`  
  Upload an image for a specific wardrobe item.

---

## Chat

Endpoints for managing AI chat sessions and messages.

- **POST** `/api/chat/chat/sessions`  
  Initiate a new chat session.

- **GET** `/api/chat/chat/sessions`  
  Retrieve a list of existing chat sessions.

- **POST** `/api/chat/chat/{session_id}/message`  
  Send a message in a specific chat session.

- **GET** `/api/chat/chat/{session_id}`  
  Retrieve the message history of a specific chat session.

- **DELETE** `/api/chat/chat/{session_id}`  
  Terminate and remove a specific chat session.

---

## Additional Information

- **Authentication**:  
  All endpoints, except for `/api/register` and `/api/login`, require JWT-based authentication. Include the `Authorization: Bearer <access_token>` header in your requests.

- **API Documentation**:  
  Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

- **Error Handling**:  
  The API uses standard HTTP status codes to indicate the success or failure of requests. Error responses include a `detail` field with more information.

- **Data Formats**:  
  All request and response bodies are in JSON format, except for endpoints that handle file uploads, which use `multipart/form-data`.

---

