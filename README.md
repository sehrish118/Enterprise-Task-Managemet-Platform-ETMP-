# WorkFlow-X — Enterprise Task Management Platform (ETMP)

A production-grade, multi-tenant SaaS application for organization-based task and project management — built as a flagship full-stack engineering portfolio project. Features a high-performance REST API backend paired with a React Single Page Application (SPA), sharing a centralized business logic layer and an RBAC-aware RAG chatbot assistant.

---

## Tech Stack

### Backend
- **FastAPI** (fully async)
- **PostgreSQL + SQLAlchemy 2.0** (async, via `asyncpg`) with the **pgvector** extension enabled directly on the local database (no separate vector database service)
- **Alembic** (database migrations)
- **Pydantic v2** (data validation & schemas)
- **JWT Authentication** (access + refresh tokens), **bcrypt** password hashing
- Custom **Role-Based Access Control (RBAC)**
- **Redis + Celery** (background jobs — document processing, embedding generation)
- **LangChain + GROQ + SentenceTransformers** (RAG chatbot)

### Frontend
- **React + Vite + Tailwind CSS** — Modern SPA
- JWT stored/handled securely, **Axios** API client with auto-token injection and automatic 401 interceptors
- **react-markdown + remark-gfm** for rendering assistant responses (tables, formatting)

### Infra
- **PostgreSQL** and **Redis** run as native local services (not containerized) — the `pgvector` extension is installed directly on the local PostgreSQL server and enabled via an Alembic migration (`CREATE EXTENSION IF NOT EXISTS vector;`)
- **Celery worker** runs with the `solo` execution pool for Windows compatibility (`celery -A app.core.celery_app worker --loglevel=info --pool=solo`)

---

## Architecture

```
React SPA (frontend/) ──────► REST API (app/api/v1) ──────► Services ──────► Repositories ──────► Models (ORM)
```

The frontend interacts exclusively with the FastAPI REST API endpoints over HTTP.

**Architectural Layers:**
- **Routers** (`app/api/v1/`) — Thin HTTP concerns only (request parsing, status codes, response serialization), no direct business logic.
- **Services** (`app/services/`) — Central business logic layer, handles validations, permission checks, and domain exceptions.
- **Repositories** (`app/repositories/`) — Pure data access layer executing database queries via SQLAlchemy async sessions.
- **Models** (`app/models/`) — Database schemas and relationships mapped with SQLAlchemy ORM.

The RAG chatbot follows the same principle: it never re-implements permission logic. Its "tools" are thin wrappers that call the **same Services** the REST API uses, so RBAC rules are enforced in exactly one place.

---

## Project Structure

```
ETMP/
├── app/
│   ├── main.py                # Entry point, API routers registered here
│   ├── core/                  # Config, security (JWT/bcrypt), logging, exceptions,
│   │                           # celery_app, rate_limit (chatbot-specific)
│   ├── db/                    # Session, declarative base, RBAC seed data
│   ├── models/                # SQLAlchemy models (incl. Document, ChatSession,
│   │                           # ChatMessage, DocumentEmbedding)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── repositories/           # Data access layer
│   ├── services/                # Business logic layer
│   ├── api/v1/                   # REST API JSON endpoints — consumed by React frontend
│   ├── middleware/                # IP-based rate limiting, CORS, request logging
│   ├── enums/permissions.py        # Central RBAC permission registry
│   └── rag/                         # RAG chatbot module
│       ├── embedding_service.py     # SentenceTransformers wrapper (singleton model load)
│       ├── text_extraction.py       # PDF/DOCX/TXT text extraction
│       ├── chunking.py              # Overlapping word-based chunking
│       ├── relevance_check.py       # LLM gate: rejects non-company-related uploads
│       ├── tasks.py                 # Celery tasks (embed task/comment, process document)
│       ├── rbac_scope.py            # Resolves a user's allowed org/project scope
│       ├── tools.py                 # Structured-query tools (wrap existing Services)
│       ├── retrieval.py             # RBAC-scoped pgvector similarity search + citations
│       └── chat_service.py          # LangChain + GROQ orchestration, streaming
├── alembic/                    # Database migrations
└── frontend/                   # React SPA
    └── src/
        ├── api/client.js             # Axios client with JWT auto-attach & 401 handling
        ├── context/AuthContext.jsx   # Global user/session state
        ├── components/               # Card, Button, Input, Navbar, Sidebar, ProtectedRoute
        └── pages/                    # Login, Register, AcceptInvite, Dashboard,
                                       # Organizations, Teams, Projects, Tasks,
                                       # Notifications, Profile, OrgDashboard,
                                       # ActivityLogs, Assistant (chatbot UI)
```

---

## Multi-Tenancy & Invitation Flow

### Multi-Tenancy Architecture
Every tenant-scoped table carries a denormalized `organization_id` column. Users can belong to multiple organizations; access and permissions are evaluated per-organization rather than globally.

### User Onboarding & Invitation Flow
- **Adding/Inviting Members:** Org Owners/Admins invite members to teams by specifying their Full Name, Email, and Role (MEMBER / TEAM_LEAD).
- **Direct Add vs. Secure Invite:**
  - If the user is already part of the organization, they are attached directly.
  - If the user is new, an invitation link containing an encoded, secure token is generated.
- **Accepting Invitation:** The invited user accesses the link (`/accept-invite?token=...`), which pre-identifies them without requiring re-entry of their name, and allows them to securely set their password to complete onboarding.

---

## Role-Based Access Control (RBAC) — Full Permission Matrix

Three organization-level roles: **Owner**, **Admin**, **Member**. One project-scoped role, independent of org role: **Project Manager**.

| Action | Owner | Admin | Member |
|---|---|---|---|
| Create an organization | ✅ (anyone) | ✅ | ✅ |
| View/update organization settings | ✅ | ✅ | ❌ |
| Add/manage organization members & send invitations | ✅ | ✅ | ❌ |
| Delete organization | ✅ | ❌ | ❌ |
| View organization dashboard / activity logs | ✅ | ✅ | ❌ |
| Deactivate / reactivate a user | ✅ | ✅ | ❌ |
| Create a team | ✅ | ✅ | ❌ |
| Update/delete a team, manage team members | ✅ | ✅ | ❌ |
| View teams (read-only) | ✅ | ✅ | ✅ |
| Create a project | ✅ | ✅ | ✅ (creator auto-becomes Project Manager) |
| View all projects in the org | ✅ | ✅ | ❌ (see below) |
| Upload a document to the org knowledge base | ✅ | ✅ | ❌ |
| Create / update a task | ✅ | ✅ | ✅ |
| Delete / assign a task | Only if Project Manager | Only if Project Manager | Only if Project Manager |
| Post a comment | ✅ Any authenticated org member | | |
| Edit/delete a comment | ✅ Only the comment's own author (ownership check) | | |

**Project-Level Visibility Rules:**
- Owners & Admins can view every project within the organization.
- Members can only view projects to which they are explicitly assigned. Accessing an unassigned project returns `404 Not Found` (rather than `403`) to prevent resource enumeration.
- Project creators automatically assume the Project Manager role for that specific project.

**Technical Enforcement:**
- REST API requests authenticate via JWT passed in the `Authorization: Bearer <token>` header.
- `require_permission()` inspects the user's role-permission mapping using a single joined query: `organization_members → roles → role_permissions → permissions`.
- Project-level actions (task assignment, task deletion) check `project_members.role == PROJECT_MANAGER` directly within the service layer.
- The chatbot never re-derives these rules — it calls the same `Service` methods, so a Member gets exactly the same visibility through the chatbot as they do through the REST API.

---

## RAG Chatbot

An in-app AI assistant scoped per-organization, accessible from a dedicated **Assistant** tab within each organization.

### Core Capabilities
- **Structured data queries** — member counts, team rosters, project/task lists, per-user task assignments, and org/personal dashboards, answered via function-calling into the existing Service layer (no query logic is duplicated).
- **Document Q&A (RAG)** — uploaded documents, task descriptions, and comments are chunked, embedded with SentenceTransformers, and stored in `pgvector`. Retrieval uses RBAC-filtered cosine similarity search, and answers include a source citation (e.g. *"Source: Task: Fix login bug"*).
- **Relevance gate on upload** — before a newly uploaded document is chunked and embedded, an LLM classification step checks whether its content is plausibly company/work-related. Unrelated uploads (e.g. a recipe) are marked `REJECTED` and never enter the searchable knowledge base.
- **Multi-turn conversations** — each user can maintain multiple named chat sessions per organization (persisted in `chat_sessions` / `chat_messages`), switchable from a sidebar, with automatic title generation from the first message.
- **Streaming responses** — answers stream token-by-token over Server-Sent Events (SSE) for a responsive, ChatGPT-style experience.
- **Prompt-injection resistant** — content retrieved from documents/tasks/comments is treated strictly as data; the system prompt explicitly instructs the model to ignore any embedded instructions found in retrieved content.
- **Per-user rate limiting** — a Redis-backed limiter caps chatbot messages per user per minute, independent of the general IP-based API rate limiter.

### RBAC Enforcement in the Chatbot
Every chatbot query — whether a structured tool call or a document search — is resolved against a `ChatbotScope` (`app/rag/rbac_scope.py`) built from the requesting user's actual organization/project memberships. Members are restricted to their own tasks and their own projects' data; organization-wide statistics (total member count, org dashboard) are limited to Owners/Admins — mirroring the REST API's permission matrix exactly, with no separate rule set to maintain.

---

## Local Setup

### Prerequisites
- Python 3.11+ and Node.js
- **PostgreSQL** installed locally, with the `pgvector` extension available on the server (installed via `apt install postgresql-<version>-pgvector` on Linux, or built from source / installed via `brew install pgvector` on macOS)
- **Redis** installed and running locally (not containerized)
- A [GROQ](https://console.groq.com) API key (free tier available)

### Backend Setup

```bash
# Clone the repository and copy environment template
cp .env.example .env

# Create and activate Python virtual environment
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell (or source venv/bin/activate on Linux/Mac)

# Install dependencies
pip install -r requirements.txt

# Run migrations (this also enables the pgvector extension on your local database)
# & seed RBAC roles/permissions
alembic upgrade head
python -m app.db.seed

# Start the FastAPI development server
uvicorn app.main:app --reload
```

### Background Worker (required for embeddings & document processing)

In a separate terminal:

```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

> The `--pool=solo` flag is required on Windows — Celery's default prefork/gevent pools conflict with the project's async (`asyncpg`) database connections and cause tasks to hang.

### React Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access Endpoints
- REST API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- React Frontend: [http://localhost:5173](http://localhost:5173)

---

## Development Approach

Built module-by-module using dedicated feature branches, with end-to-end API validation using Postman and client testing via the React interface. RBAC security was continuously validated using multi-account audit suites across all role levels (Owner, Admin, Member, Project Manager). The RAG chatbot was built as a layered extension on top of the existing service architecture, deliberately reusing (rather than duplicating) all existing permission logic.

---

## Roadmap Status

- ✅ Auth (JWT Access/Refresh, Password Hashing)
- ✅ User Onboarding & Secure Invite Flow
- ✅ Multi-Tenant Isolation & Custom RBAC Matrix
- ✅ Teams, Projects, Tasks, and Comments Management
- ✅ Notifications & Audit Activity Logs
- ✅ Global Exception Handling & Input Validation (Pydantic v2)
- ✅ React SPA Frontend (Tailwind CSS, Axios Integration)
- ✅ RAG Chatbot — structured queries, document Q&A with citations, RBAC-scoped retrieval, streaming responses, multi-session chat history, document upload with relevance filtering, per-user rate limiting
- 🔲 Remaining: Automated test suite (Pytest & Vitest), production deployment setup, semantic caching, hybrid (keyword + semantic) search