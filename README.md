# 🎫 Help Desk Ticketing System

A full-stack Help Desk Ticketing System built with Python, Flask, PostgreSQL, and Docker Compose.

## Features

- 🔐 User registration and login
- 🎫 Create, view, edit, delete tickets
- 💬 Comments on tickets
- ⚡ Ticket priority (Low, Medium, High)
- 🔄 Ticket status workflow (Open → In Progress → Closed)
- 👑 Admin dashboard with statistics
- 🔒 Role-based access control (Admin vs User)
- 🔍 Search and filter tickets by title, status, priority
- 📎 File attachments (PNG, JPG, PDF, DOC, DOCX)
- 📧 Real email notifications via Gmail SMTP
- 🐳 Docker Compose deployment

## Tech Stack

- Python 3.12
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Login
- Flask-Mail
- Bootstrap 5
- Docker Compose

## Run with Docker Compose

1. Clone the repository:
git clone https://github.com/GK1023PRO/helpdesk-system.git

cd helpdesk-system

2. Create a `.env` file:
MAIL_USERNAME=your_gmail@gmail.com

MAIL_PASSWORD=your_gmail_app_password

3. Start the app:
docker-compose up --build

4. Visit: http://127.0.0.1:5004

5. Register an account and make it admin:
docker exec -it helpdesk-system-db-1 psql -U admin -d helpdesk

UPDATE users SET role='admin' WHERE username='your_username';

\q

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| MAIL_USERNAME | Gmail address for sending emails |
| MAIL_PASSWORD | Gmail App Password (16 characters) |

## Database Design

### Users Table
| Column | Type |
|--------|------|
| id | Integer |
| username | String |
| email | String |
| password | String (hashed) |
| role | String (user/admin) |

### Tickets Table
| Column | Type |
|--------|------|
| id | Integer |
| title | String |
| description | Text |
| priority | String (Low/Medium/High) |
| status | String (Open/In Progress/Closed) |
| filename | String (attachment) |
| receiver_email | String (notification recipient) |
| created_at | DateTime |
| user_id | ForeignKey |

### Comments Table
| Column | Type |
|--------|------|
| id | Integer |
| content | Text |
| created_at | DateTime |
| user_id | ForeignKey |
| ticket_id | ForeignKey |

## Notes

- Admin dashboard shows total, open, in progress, and closed ticket counts
- Only admins can see all tickets; users only see their own
- Passwords are securely hashed using Werkzeug
- Email notifications sent on ticket creation and updates
- Credentials stored securely in .env file