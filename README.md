# simple-projectmgmt
Simple Kanban, Product Backlog and KPI pages


# Project Management Dashboard Backend

A Flask-based backend with SQLite database for managing KPIs, Kanban tasks, product backlog, and QR code generation.

## Features

- **KPI Dashboard**: Track and manage key performance indicators
- **Kanban Board**: Manage tasks with To Do, Doing, and Done columns
- **Product Backlog**: Manage product backlog items with priorities and story points
- **QR Code Generator**: Generate QR codes for any text input
- **RESTful API**: Clean API endpoints for all operations
- **SQLite Database**: Lightweight, file-based database

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Frontend: http://localhost:8000
   - API Base URL: http://localhost:8000/api

## API Endpoints

### KPI Endpoints

- `GET /api/kpis` - Get all KPIs
- `POST /api/kpis` - Create a new KPI

**KPI Data Structure:**
```json
{
  "metric_name": "Revenue",
  "value": 45000,
  "target_value": 50000,
  "category": "financial"
}
```

### Task Endpoints (Kanban)

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task

**Task Data Structure:**
```json
{
  "title": "Setup Authentication",
  "description": "Implement user login system",
  "status": "todo",
  "priority": "high",
  "assignee": "John Doe",
  "story_points": 5,
  "detailed": "Yes",
  "estimable": "Yes",
  "emergent": "No",
  "prioritized": "Yes"
}
```

### Backlog Endpoints

- `GET /api/backlog` - Get all backlog items
- `POST /api/backlog` - Create a new backlog item
- `PUT /api/backlog/<id>` - Update a backlog item
- `DELETE /api/backlog/<id>` - Delete a backlog item

**Backlog Item Data Structure:**
```json
{
  "title": "User Registration",
  "description": "Allow users to create accounts",
  "priority": 1,
  "story_points": 5,
  "status": "new",
  "epic": "Authentication"
}
```

### QR Code Endpoint

- `POST /api/qr` - Generate QR code

**QR Code Request:**
```json
{
  "text": "Hello World"
}
```

**QR Code Response:**
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

## Database Schema

### KPIs Table
- `id` (PRIMARY KEY)
- `metric_name` (TEXT)
- `value` (REAL)
- `target_value` (REAL)
- `date` (DATE)
- `category` (TEXT)

### Tasks Table
- `id` (PRIMARY KEY)
- `title` (TEXT)
- `description` (TEXT)
- `status` (TEXT: 'todo', 'doing', 'done')
- `priority` (TEXT: 'low', 'medium', 'high')
- `assignee` (TEXT)
- `created_date` (DATE)
- `updated_date` (DATE)
- `story_points` (INTEGER)
- `detailed` (TEXT: 'Yes', 'No')
- `estimable` (TEXT: 'Yes', 'No')
- `emergent` (TEXT: 'Yes', 'No')
- `prioritized` (TEXT: 'Yes', 'No')

### Backlog Items Table
- `id` (PRIMARY KEY)
- `title` (TEXT)
- `description` (TEXT)
- `priority` (INTEGER)
- `story_points` (INTEGER)
- `status` (TEXT)
- `epic` (TEXT)
- `created_date` (DATE)
- `updated_date` (DATE)

## Configuration

The application uses configuration from `config.py`. You can set environment variables:

- `SECRET_KEY`: Secret key for Flask (default: 'dev-secret-key-change-in-production')
- `DATABASE_URL`: Path to SQLite database (default: 'project_management.db')

## Development

### Database Utilities

The `database.py` file provides utility functions for database operations:

- `get_db_connection()`: Get database connection
- `execute_query()`: Execute SQL queries
- `backup_database()`: Create database backups
- `get_all_tables()`: List all tables

### Sample Data

The application automatically creates sample data on first run:

- Sample KPIs for Revenue, Customer Satisfaction, and Conversion Rate
- Sample tasks for authentication, database design, and testing
- Sample backlog items for user registration and analytics

## Production Deployment

For production deployment:

1. Set `SECRET_KEY` environment variable
2. Use `ProductionConfig` in `config.py`
3. Consider using a more robust database like PostgreSQL
4. Set up proper logging and monitoring
5. Use a production WSGI server like Gunicorn

## Testing

You can test the API endpoints using tools like:

- Postman
- curl
- Python requests library
- Browser for GET endpoints

Example curl command:
```bash
curl -X GET http://localhost:5000/api/tasks
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` or kill the process using port 5000
2. **Database locked**: Close any other connections to the database file
3. **Module not found**: Make sure virtual environment is activated and dependencies are installed

### Logs

The application runs in debug mode by default and will show detailed error messages in the console.

## License

This project is for educational/development purposes. 