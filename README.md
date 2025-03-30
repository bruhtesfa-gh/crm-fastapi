# CRM FastAPI Backend

A robust CRM (Customer Relationship Management) backend system built with FastAPI, featuring lead management, quotation workflow, and role-based access control.

## Features

- **Lead Management**

  - Complete lead lifecycle (New → Contacted → Qualified → Lost)
  - Lead information tracking and validation
  - Lead assignment to sales representatives

- **Quotation System**

  - Full quotation workflow (Draft → Submitted → Approved → Sent → Accepted/Rejected)
  - Manager approval process
  - Version tracking and history

- **User Management**

  - Role-based access control (Admin, Manager, Sales Rep)
  - Secure authentication using JWT
  - User activity tracking

- **Audit Logging**
  - Comprehensive audit trail
  - Before/after value tracking
  - User action history

## Technology Stack

- FastAPI (Modern, fast web framework)
- SQLAlchemy (Async ORM)
- Pydantic (Data validation)
- PostgreSQL (Database)
- Alembic (Database migrations)
- pytest (Testing framework)

## Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/bruhtesfa-gh/crm-fastapi.git
cd crm-fastapi
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install poetry
poetry install
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Database Setup

1. Create database:

```bash
createdb crm_db
```

2. Run migrations:

```bash
make seed
```

## Running the Application

### Development

```bash
uvicorn app.main:app --reload
```

### Production

```bash
make run
```

### Docker

```bash
docker-compose up -d
```

## API Documentation

Once running, access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Project Structure
