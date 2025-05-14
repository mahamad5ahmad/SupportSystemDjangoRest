# Support Ticket System API

> ⚠️ **Note on Asynchronous Support**

This project is currently built using **standard synchronous Django views and configuration**. As such, API requests are handled synchronously by default, which is sufficient for many use cases but may not scale optimally for high-concurrency scenarios.

To enable full **asynchronous (non-blocking) request handling**, the following changes are required:

1. **Run Django using an ASGI server**, such as `uvicorn` or `daphne`, instead of the default WSGI server.
2. **Convert views to asynchronous views**, using `async def` along with DRF's `APIView` or compatible async-compatible classes.
3. **Use `async`-compatible database drivers and ORM layers** (e.g., `databases` or `Tortoise ORM` if not using Django ORM).
4. **Write asynchronous tests** using libraries like `pytest-asyncio` or `httpx` instead of Django's default test client.
5. **Ensure middleware and third-party packages are compatible** with async execution.

This shift to an async stack allows for better performance under heavy I/O loads (e.g., external APIs, file operations), but requires careful consideration and proper async design patterns throughout the application.

For now, the application is fully functional in a synchronous context.


## Features
- 🛡️ Admin: CRUD tickets
- 👨‍💻 Agents: Fetch & manage assigned tickets (max 15)
- 📊 Status tracking: Open → Assigned → Resolved → Closed

## API Endpoints
| Method | Endpoint                | Role   | Description                     |
|--------|-------------------------|--------|---------------------------------|
| POST   | `/api/tickets/`         | Admin  | Create ticket                   |
| GET    | `/api/tickets/`         | Admin  | List all tickets                |
| GET    | `/api/tickets/{id}/`    | Admin  | Get ticket details              |
| PUT    | `/api/tickets/{id}/`    | Admin  | Update ticket                   |
| DELETE | `/api/tickets/{id}/`    | Admin  | Delete ticket                   |
| GET    | `/api/agent/tickets/`   | Agent  | Get assigned tickets (max 15)   |
| POST   | `/api/agent/tickets/`   | Agent  | Update ticket status            |

## Quick Start
```bash
# 1. Setup
git clone https://github.com/yourusername/support-ticket-system.git
cd support-ticket-system
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 2. Configure
# Edit settings.py for your database

# 3. Initialize
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Unit tests
python manage.py test

## ERD
+---------------+       +----------------+       +-----------------+
|     User      |       |     Ticket     |       | TicketAssignment|
+---------------+       +----------------+       +-----------------+
| id (PK)       |       | id (PK)        |       | id (PK)         |
| username      |       | title          |       | ticket (FK)     |
| email         |       | description    |       | agent (FK)      |
| password      |       | status         |       | assigned_at     |
| is_staff      |       | created_at     |       | is_active       |
| is_superuser  |       | updated_at     |       +-----------------+
+---------------+       | created_by (FK)|
                        +----------------+

