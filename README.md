# Support Ticket System API

## Features
- 🛡️ Admin: CRUD tickets
- 👨‍💻 Agents: Fetch & manage assigned tickets (max 15)
- ⚡ Concurrency-safe assignment
- 📊 Status tracking: Open → Assigned → In Progress → Resolved → Closed

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

