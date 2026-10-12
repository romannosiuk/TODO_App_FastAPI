# TodoApp — FastAPI

A full-stack to-do list application built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**. It offers a REST API secured with JWT authentication and a server-rendered web UI (Jinja2 + Bootstrap) for managing personal tasks.

## Features

- User registration and login with **JWT** tokens (OAuth2 password flow, bcrypt-hashed passwords)
- Create, read, update and delete to-dos with title, description, priority (1–5) and completion status
- Each user sees and edits only their own to-dos
- **Admin** role: view all to-dos, delete any to-do, look up user info
- User profile endpoints: view profile, change password, update phone number
- Web UI with login, registration, to-do list, add and edit pages
- Database migrations with **Alembic**
- Test suite with **pytest** using an isolated SQLite database

## Tech Stack

| Layer          | Technology                                |
|----------------|-------------------------------------------|
| Web framework  | FastAPI, Starlette, Uvicorn               |
| Database / ORM | PostgreSQL, SQLAlchemy 2, Alembic         |
| Auth           | python-jose (JWT), passlib + bcrypt       |
| Configuration  | python-dotenv (`.env`)                    |
| Validation     | Pydantic v2                               |
| Frontend       | Jinja2 templates, Bootstrap, vanilla JS   |
| Testing        | pytest, pytest-asyncio, FastAPI TestClient |

## Project Structure

```
TodoApp_FastApi/
├── .env.example           # Template for environment variables
├── render.yaml            # Render deployment Blueprint
├── requirements.txt
└── TodoApp/
    ├── main.py            # FastAPI app, static files, router registration
    ├── database.py        # SQLAlchemy engine and session
    ├── models.py          # Users and Todos models
    ├── alembic.ini        # Alembic configuration
    ├── alembic/           # Migration scripts
    ├── routers/
    │   ├── auth.py        # Registration, login (JWT), auth pages
    │   ├── todos.py       # To-do CRUD API and UI pages
    │   ├── users.py       # Current-user profile endpoints
    │   └── admin.py       # Admin-only endpoints
    ├── templates/         # Jinja2 HTML templates
    ├── static/            # CSS and JavaScript (Bootstrap, base.js)
    └── test/              # pytest test suite
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL running locally

### Installation

```bash
git clone <repository-url>
cd TodoApp_FastApi

python -m venv fastapienv
source fastapienv/bin/activate      # Windows: fastapienv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Settings are loaded from a `.env` file in the project root (via `python-dotenv`). Copy the template and fill in your values:

```bash
cp .env.example .env
```

| Variable                  | Description                                   | Example                                                      |
|---------------------------|-----------------------------------------------|--------------------------------------------------------------|
| `SECRET_KEY`              | Key used to sign JWT tokens                   | output of `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM`               | JWT signing algorithm                         | `HS256`                                                      |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string (app and Alembic) | `postgresql://postgres:password@localhost/TodoApplicationDataBase` |

`.env` is listed in `.gitignore` — never commit it.

### Database setup

Create a PostgreSQL database named `TodoApplicationDataBase` (or whatever name you use in `SQLALCHEMY_DATABASE_URI`).

Tables are created automatically on application startup. To apply migrations:

```bash
cd TodoApp
alembic upgrade head
```

### Running the app

Run from the project root (the static files path is relative to it):

```bash
uvicorn TodoApp.main:app --reload
```

- Web UI: <http://127.0.0.1:8000> (redirects to the to-do page / login)
- Interactive API docs (Swagger): <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## API Overview

### Auth — `/auth`

| Method | Endpoint               | Description                              |
|--------|------------------------|------------------------------------------|
| POST   | `/auth/`               | Register a new user                      |
| POST   | `/auth/token`          | Log in and receive a JWT access token    |
| GET    | `/auth/login-page`     | Login page (HTML)                        |
| GET    | `/auth/register-page`  | Registration page (HTML)                 |

### To-dos — `/todos` (authenticated)

| Method | Endpoint                         | Description                     |
|--------|----------------------------------|---------------------------------|
| GET    | `/todos/`                        | List the current user's to-dos  |
| GET    | `/todos/todo/{todo_id}`          | Get a single to-do              |
| POST   | `/todos/todo`                    | Create a to-do                  |
| PUT    | `/todos/todo/{todo_id}`          | Update a to-do                  |
| DELETE | `/todos/todo/{todo_id}`          | Delete a to-do                  |
| GET    | `/todos/todo-page`               | To-do list page (HTML)          |
| GET    | `/todos/add-todo-page`           | Add to-do page (HTML)           |
| GET    | `/todos/edit-todo-page/{todo_id}`| Edit to-do page (HTML)          |

### Users — `/users` (authenticated)

| Method | Endpoint                               | Description            |
|--------|----------------------------------------|------------------------|
| GET    | `/users/`                              | Get current user info  |
| PUT    | `/users/password/{user_id}`            | Change password        |
| PUT    | `/users/phone_number/{phone_number}`   | Update phone number    |

### Admin — `/admin` (admin role only)

| Method | Endpoint                  | Description          |
|--------|---------------------------|----------------------|
| GET    | `/admin/todo`             | List all to-dos      |
| DELETE | `/admin/todo/{todo_id}`   | Delete any to-do     |
| GET    | `/admin/{user_id}`        | Get user info        |

### Other

| Method | Endpoint   | Description   |
|--------|------------|---------------|
| GET    | `/health`  | Health check  |

### Example: obtaining a token

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=secret"
```

Use the returned `access_token` in the `Authorization: Bearer <token>` header for protected endpoints. Tokens expire after 20 minutes. The web UI stores the token in an `access_token` cookie.

### Example: to-do payload

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": 3,
  "complete": false
}
```

## Deployment (Render)

The repository includes a `render.yaml` [Blueprint](https://render.com/docs/blueprint-spec) that creates:

- a **web service** running `uvicorn TodoApp.main:app --host 0.0.0.0 --port $PORT`
- a **PostgreSQL** database, whose connection string is passed in as `SQLALCHEMY_DATABASE_URI`
- a randomly generated `SECRET_KEY`

To deploy: in the Render dashboard choose **New → Blueprint**, connect this repository and apply. Tables are created automatically on first startup.

If you create the web service manually instead, leave **Root Directory** empty, use the start command above and set the environment variables from the [Configuration](#configuration) section.

## Running Tests

Tests use a separate SQLite database (`testdb.db`) and override the database and auth dependencies, so PostgreSQL does not need to be running. A `.env` file is still required, since `SECRET_KEY` and `ALGORITHM` are read at import time:

```bash
pytest
```

## Security Notes

This is a learning / portfolio project. Before deploying it anywhere public:

- Use a strong, unique `SECRET_KEY` and real database credentials in `.env` for each environment.
- Restrict the `role` field on registration so users cannot assign themselves the `admin` role.
- Serve the app over HTTPS and consider setting the auth cookie with `Secure` / `SameSite` flags.
