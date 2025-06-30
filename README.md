# Dassyor Startup Platform 🚀

A comprehensive startup ecosystem consisting of multiple interconnected applications designed to help entrepreneurs validate ideas, manage projects, and collaborate effectively.

## 📋 Project Overview

This repository contains four main applications that work together to provide a complete startup development platform:

### 1. **Dassyor Platform API** - Core Backend Service

A Flask-based REST API that provides user authentication, project management, collaboration features, and phase-based project workflows.

### 2. **Dassyor Platform ClientApp** - Main Web Application

An Angular-based web application that provides the main user interface for project management and collaboration.

### 3. **Idea Validation Tool AI API** - AI-Powered Validation Service

A Flask API with Celery integration that provides AI-powered idea validation, market research, and automated email notifications.

### 4. **Idea Validation Tool ClientApp** - Landing Page & Validation Interface

A React-based application featuring a modern landing page, idea validation forms, and admin dashboard for managing waitlists and user submissions.

## 🏗️ Architecture Overview

The Dassyor platform follows a microservices architecture with four main components that work together to provide a comprehensive startup development ecosystem:

### Frontend Applications

**Dassyor Platform ClientApp (Angular)**

- Main web application for project management and collaboration
- Communicates with the Core API for user authentication and project operations
- Provides dashboard interface for managing projects, phases, and team collaboration
- Uses JWT tokens for secure API communication

**Idea Validation Tool ClientApp (React)**

- Landing page and idea validation interface
- Standalone application with its own Express.js backend
- Handles user submissions, waitlist management, and admin dashboard
- Integrates with OpenAI API for idea validation features

### Backend Services

**Dassyor Platform API (Flask)**

- Core backend service providing centralized user and project management
- Handles authentication, authorization, and user session management
- Manages project lifecycle, collaboration invitations, and phase progression
- Uses PostgreSQL database with SQLAlchemy ORM and Alembic migrations
- Implements JWT-based authentication with Google OAuth support

**Idea Validation Tool AI API (Flask + Celery)**

- Specialized AI service for idea validation and market research
- Processes asynchronous tasks using Celery with Redis as message broker
- Integrates with OpenAI API for intelligent idea analysis
- Provides web search capabilities and automated email notifications
- Maintains separate PostgreSQL database for task tracking

### Data Layer

**PostgreSQL Databases**

- **Dassyor Platform Database**: Stores user accounts, projects, phases, and collaboration data
- **Idea Validation Database**: Stores validation tasks, user submissions, and waitlist information
- Both databases use structured schemas with proper relationships and constraints

### Key Integration Points

1. **Authentication Flow**: Angular app → Core API → JWT tokens
2. **Project Management**: Angular app ↔ Core API ↔ PostgreSQL
3. **Idea Validation**: React app → AI API → Celery tasks → OpenAI
4. **Email Notifications**: Both APIs → SMTP services
5. **Data Sharing**: Minimal direct communication between services for loose coupling

### Technology Stack Summary

- **Frontend**: Angular 19, React 18, TypeScript
- **Backend**: Flask, Express.js, Celery
- **Database**: PostgreSQL (2 separate instances)
- **Message Queue**: Redis
- **AI Services**: OpenAI API
- **Authentication**: JWT, Google OAuth, Passport.js
- **UI Frameworks**: PrimeNG, Shadcn UI, Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18+)
- **Python** (3.8+)
- **PostgreSQL** (12+)
- **Redis** (for Celery tasks)
- **OpenAI API Key** (for AI features)

### Environment Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd dassyor-project
   ```

2. **Set up environment variables**

   Create `.env` files in each project directory with the following variables:

   **Dassyor Platform API/.env:**

   ```env
   DB_URL=postgresql://username:password@localhost:5432/dassyor_platform
   JWT_SECRET_KEY=your_jwt_secret_key
   ISSUER=dassyor-platform
   AUDIENCE=dassyor-users
   ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000
   ```

   **Idea Validation Tool AI API/.env:**

   ```env
   CLIENT_APP_HOMEPAGE_URL=http://localhost:3000
   TASKS_ACCESS_PASSWORD=your_admin_password
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://username:password@localhost:5432/idea_validation
   REDIS_URL=redis://localhost:6379
   ```

   **Idea Validation Tool ClientApp/.env:**

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/idea_validation
   SESSION_SECRET=your_session_secret
   OPENAI_API_KEY=your_openai_api_key
   VITE_ADMIN_ROUTE=admin
   ```

## 📁 Project Details

### 1. Dassyor Platform API

**Purpose:** Core backend service providing user management, project collaboration, and phase-based workflows.

**Key Features:**

- 🔐 JWT-based authentication with Google OAuth support
- 👥 Project collaboration with invitation system
- 📋 Phase-based project management (10 predefined phases)
- 📧 Email notifications and templates
- 🔄 Database migrations with Alembic
- 📊 Comprehensive logging and error handling

**Tech Stack:**

- **Backend:** Flask, SQLAlchemy, Alembic
- **Database:** PostgreSQL
- **Authentication:** JWT, Google OAuth
- **Email:** SMTP with template system
- **Validation:** Pydantic models

**Setup:**

```bash
cd "Dassyor Platform API"
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd src
flask db upgrade
python -m flask run
```

**API Endpoints:**

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /projects` - List user's projects
- `POST /projects` - Create new project
- `POST /projects/{id}/invite` - Invite collaborators
- `GET /phases/projects/{id}` - Get project phases
- `POST /phases/projects/{id}/phases/{phase_id}/complete` - Complete phase

### 2. Dassyor Platform ClientApp

**Purpose:** Main web application for project management and collaboration.

**Key Features:**

- 🎨 Modern UI with PrimeNG components
- 📱 Responsive design with Tailwind CSS
- 🔐 Protected routes with role-based access
- 📊 Dashboard with project overview
- 👥 Collaboration management interface

**Tech Stack:**

- **Frontend:** Angular 19, TypeScript
- **UI Components:** PrimeNG, Tailwind CSS
- **Authentication:** Angular Social Login
- **Routing:** Angular Router with guards

**Setup:**

```bash
cd "Dassyor Platform ClientApp"
npm install
ng serve
```

**Available Routes:**

- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/error/403` - Forbidden page
- `/error/404` - Not found page

### 3. Idea Validation Tool AI API

**Purpose:** AI-powered service for idea validation and market research.

**Key Features:**

- 🤖 OpenAI integration for idea analysis
- 🔍 Web search capabilities
- 📧 Automated email notifications
- ⚡ Asynchronous task processing with Celery
- 📊 Task status tracking
- 🔐 Basic authentication for admin access

**Tech Stack:**

- **Backend:** Flask, Celery
- **AI:** OpenAI API
- **Database:** PostgreSQL
- **Task Queue:** Redis + Celery
- **Web Scraping:** BeautifulSoup, Requests

**Setup:**

```bash
cd "Idea Validation Tool AI API"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Redis (required for Celery)
redis-server

# Start Celery worker (in new terminal)
celery -A src.celery_config worker --loglevel=info

# Start Flask app
python src/app.py
```

**API Endpoints:**

- `POST /api/v1/search` - Submit idea for validation
- `GET /api/v1/tasks/{task_id}` - Get task status (admin)
- `GET /api/v1/tasks` - List all tasks (admin)

### 4. Idea Validation Tool ClientApp

**Purpose:** Landing page and idea validation interface with admin dashboard.

**Key Features:**

- 🎯 Modern landing page with animations
- 📝 Idea validation forms
- 📧 Newsletter/waitlist system
- 🔐 Admin dashboard with authentication
- 📊 Excel export functionality
- 🎨 Beautiful UI with Shadcn components

**Tech Stack:**

- **Frontend:** React 18, TypeScript
- **UI Components:** Shadcn UI, Radix UI
- **Styling:** Tailwind CSS, Framer Motion
- **Backend:** Express.js
- **Database:** PostgreSQL with Drizzle ORM
- **Authentication:** Passport.js with bcrypt

**Setup:**

```bash
cd "Idea Validation Tool ClientApp"
npm install
npm run db:push
npm run dev
```

**Available Routes:**

- `/` - Landing page
- `/validate` - Idea validation form
- `/terms` - Terms of service
- `/privacy` - Privacy policy
- `/admin/login` - Admin login
- `/admin/dashboard` - Admin dashboard (protected)

## 🔄 Project Phases

The platform implements a structured 10-phase approach to startup development:

1. **Identify Problem** - Define the core problem
2. **Problem Scale** - Understand scope and scale
3. **Problem Impact** - Assess consequences
4. **Current Solutions** - Research existing solutions
5. **Audience Targeting** - Define target audience
6. **Define Product** - Product requirements
7. **Verify Demand** - Market validation
8. **Business Strategy** - Business model development
9. **Branding** - Brand identity creation
10. **Build Product** - Product development

## 🛠️ Development Commands

### Database Management

```bash
# Dassyor Platform API
cd "Dassyor Platform API/src"
flask db migrate -m "migration message"
flask db upgrade

# Idea Validation Tool ClientApp
cd "Idea Validation Tool ClientApp"
npm run db:push
```

### Code Quality

```bash
# Python formatting
black .
isort .

# TypeScript checking
npm run check
```

### Testing

```bash
# Angular tests
cd "Dassyor Platform ClientApp"
ng test

# React tests
cd "Idea Validation Tool ClientApp"
npm test
```

## 🚢 Deployment

### Docker Support

The Idea Validation Tool includes Docker configuration:

```bash
cd "Idea Validation Tool AI API"
docker-compose up -d
```

### Production Considerations

- Set `NODE_ENV=production` for production builds
- Configure secure session secrets
- Use HTTPS in production
- Set up proper CORS origins
- Configure database connection pooling
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the individual project README files for specific documentation

---

**Dassyor** - Empowering entrepreneurs to build successful startups through structured guidance and AI-powered validation.
