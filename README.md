# Entrepreneurship Social Platform — Backend (Django/DRF)

Backend for a social platform with auth, profiles, projects, posts, comments, likes, follow system, search, and real-time chat/notifications.

**Tech:** Django, Django REST Framework, Redis, Celery, Channels/WebSockets

## Features
- **Authentication**: JWT-based (or session) authentication.
- **Social Graph**: Follow/unfollow system with efficient querying.
- **Real-time**: WebSocket integration for chat and notifications (Django Channels).
- **Async Tasks**: Celery with Redis for background processing (e.g., email notifications).

## Quickstart
### Prerequisites
- Python 3.10+
- Redis (for Celery/Channels)

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Migrations
```bash
python manage.py migrate
```

### Run Server
```bash
python manage.py runserver
```

## Running Async Workers
```bash
docker compose up -d redis
celery -A <project_name> worker -l info
```

## Testing
```bash
pytest
```
