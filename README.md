# PerioCare AI Assistant Overview

**PerioCare AI Assistant** is an AI-powered voice solution tailored for periodontal practices. It streamlines patient communication while maintaining a professional and empathetic tone.

## Key Features

### Dental Intelligence
- Understands **periodontal-specific terminology**.
- **Assesses urgency levels accurately** using custom-trained models.

### Autonomous Care
- Automatically handles **90% of patient interactions**.
- Significantly reduces manual involvement for routine needs.

### Smart Escalation
- **Escalates only critical or genuinely urgent cases** to human staff.
- Ensures on-call resources are used efficiently.

> The assistant delivers a seamless patient experience that is  
> **human-like, respectful**, and **professionally trained in periodontal care.**

---

# Source Code Structure

The project is a Django-based application structured for clarity, modularity, and maintainability.

## Src/
The root folder containing the main database, management script, and project modules.

### db.sqlite3
- SQLite database file storing app data during development.

### manage.py
- Django CLI tool for running development server, migrations, and other commands.

---

## backend/
Contains the main Django app logic, models, views, and routes.

### admin.py
- Registers data models with Django Admin.

### apps.py
- App configuration (e.g., `BackendConfig` class).

### models.py
- Defines Django ORM models such as:
  - `UserProfile`
  - `ChatHistory`
  - `UrgencyAssessment`

### tests.py
- Unit and integration tests for backend functionality.

### urls.py
- Defines URL patterns for backend views and APIs.

### views.py
- Implements core business logic: request handling, AI integrations, responses.

### __init__.py
- Marks the directory as a Python package.

#### migrations/
- Stores Django migration files for database schema changes.

##### __init__.py
- Initializes the migrations package.

##### __pycache__/
- Compiled Python files for performance optimization.

---

## config/
Handles global Django settings, deployment configuration, and URL routing.

### asgi.py
- Entry point for asynchronous server setups (e.g., WebSocket).

### settings.py
- Global configuration for:
  - Installed apps
  - Middleware
  - Templates
  - Database settings
  - Static files
  - AI service credentials or paths

### urls.py
- Root URL configuration connecting internal apps and views.

### wsgi.py
- Entry point for WSGI-compatible web servers (e.g., Gunicorn).

### __init__.py
- Initializes the configuration package.

#### __pycache__/
- Python bytecode files for faster imports.

---

## static/
Contains CSS and static assets used by frontend templates.

### index.css
- Main stylesheet for UI design and branding.

#### images/
- `ai-assistant-avatar.png`: Visual representation of the AI assistant.

---

## templates/
Organized set of Django HTML templates for rendering pages.

### authentication/
- `login.html`: Form interface for user/staff login.

### base/
- `index.html`: Base layout for shared structure (header, footer, etc.).

### components/
Modular UI templates rendered inside views and pages:
- `assessment.html`: Displays AI-based assessments.
- `call.html`: Template for call or telehealth interface.
- `chat.html`: Conversational UI with the AI assistant.
- `home.html`: Main dashboard for users.
- `response.html`: Renders AI-generated text or response elements.
- `summary.html`: Recap or summary view of a completed interaction.

---
