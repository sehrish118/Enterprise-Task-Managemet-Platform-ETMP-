# ETMP — Enterprise Task Management Platform

A production-grade, multi-tenant SaaS backend for organization-based task
and project management. Built as a flagship backend engineering portfolio
project, following Clean Architecture principles end-to-end — with both
a REST API and a server-side rendered (Jinja2) web interface sharing the
same business logic.

## Tech Stack

- **Framework:** FastAPI (fully async)
- **Database:** PostgreSQL + SQLAlchemy 2.0 (async, via asyncpg)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Auth:** JWT (access + refresh tokens), bcrypt password hashing
- **Authorization:** Custom RBAC (Role-Based Access Control)
- **Web Frontend:** Jinja2 server-side rendering, cookie-based sessions
- **Testing:** Pytest

## Architecture

API (routers) ─┐
├─► Services (business logic) ─► Repositories (data access) ─► Models (ORM)
Web (routers) ──┘


Both the REST API (`app/api/v1/`) and the web interface (`app/web/`)
call the **same Service classes** — business logic is written once and
reused across both entry points. This is the core Clean Architecture
benefit demonstrated in this project: swapping or adding a presentation
layer (JSON vs HTML) never required touching business logic.

- **Routers** — thin, HTTP/HTML concerns only, no business logic
- **Services** — all business logic, raises domain-specific exceptions
- **Repositories** — pure data access, no business logic
- **Models** — SQLAlchemy ORM

## Project Structure
app/
├── api/v1/ # REST API endpoints (JSON) — for external/mobile clients
├── web/ # Server-side rendered HTML routes — browser-facing
│ ├── routes/
│ └── dependencies.py # cookie-based auth (vs header-based for API)
├── templates/ # Jinja2 HTML templates
├── static/ # CSS
├── core/ # Config, security, logging, exceptions
├── db/ # Session, declarative base, RBAC seed data
├── models/ # SQLAlchemy ORM models (18 tables)
├── schemas/ # Pydantic request/response schemas
├── repositories/ # Data access layer
├── services/ # Business logic layer
├── enums/permissions.py # Central permission registry
└── tests/
alembic/ # Database migrations

## Multi-Tenancy

Every tenant-scoped table carries a denormalized `organization_id`.
Users can belong to multiple organizations; access is always evaluated
per-organization, never globally.

---

## Role-Based Access Control (RBAC) — Full Permission Matrix

Three system roles exist per organization: **Owner**, **Admin**, **Member**.
A separate, project-scoped role (**Project Manager**) governs task
assignment/deletion within a specific project, independent of the
organization-level role.

### Organization-Level Roles

| Action | Owner | Admin | Member |
|---|:---:|:---:|:---:|
| Create an organization | ✅ (anyone) | ✅ | ✅ |
| View/update organization settings | ✅ | ✅ | ❌ |
| Add/manage organization members | ✅ | ✅ | ❌ |
| Delete organization | ✅ | ❌ | ❌ |
| View organization dashboard / activity logs | ✅ | ✅ | ❌ |
| Deactivate a user | ✅ | ✅ | ❌ |
| Create a team | ✅ | ✅ | ❌ |
| Update/delete a team, manage team members | ✅ | ✅ | ❌ |
| View teams (read-only) | ✅ | ✅ | ✅ |
| Create a project | ✅ | ✅ | ✅ |
| View **all** projects in the org | ✅ | ✅ | ❌ (see below) |
| Create a task | ✅ | ✅ | ✅ |
| Update a task | ✅ | ✅ | ✅ |
| Delete a task | Only if **Project Manager** for that project | Only if **Project Manager** for that project | Only if **Project Manager** for that project |
| Assign a task to someone | Only if **Project Manager** for that project | Only if **Project Manager** for that project | Only if **Project Manager** for that project |
| Post a comment | ✅ Any authenticated org member | | |
| Edit/delete a comment | ✅ Only the comment's own author (not RBAC — ownership check) | | |

### Project-Level Visibility (Independent of Org Role)

- **Owner / Admin** (anyone with `organization:manage_settings`) see **every project** in the organization.
- **Member** sees **only projects they are an explicit member of**. Guessing another project's URL returns `404 Not Found` (not `403`) — the API never confirms a project exists to a non-member.
- Whoever **creates** a project is automatically added as that project's **Project Manager**.

### Why "Project Manager" Matters

Task assignment and deletion are deliberately **not** governed by the
organization role. Even an **Organization Owner cannot assign or delete
a task** in a project unless they are specifically that project's
Project Manager. This models how real teams work: org-wide authority
doesn't automatically grant control over every individual project's
day-to-day execution.

### Permission Codes (Backend Reference)

All permissions follow a `resource:action` convention, defined centrally
in `app/enums/permissions.py`:
organization:manage_members, organization:manage_settings, organization:delete
team:create, team:manage_members, team:delete
project:create, project:manage_members, project:delete
task:create, task:update, task:delete, task:assign


These are seeded into the database via `app/db/seed.py`, mapped to the
three system roles. Task `delete`/`assign` are enforced at the service
layer via project membership role, not this table — see above.

---

## How Permission Enforcement Works (Technical)

1. **Authentication** — JWT decoded from either an `Authorization` header (REST API) or an `httponly` cookie (web), depending on entry point.
2. **Authorization** — a `require_permission()` (API) / `require_permission_web()` (web) FastAPI dependency checks the requester's role-permission mapping for the organization in the URL, via a single-query join: `organization_members → roles → role_permissions → permissions`.
3. **Project-scoped actions** (assign/delete tasks) bypass the org-level permission table entirely and check `project_members.role == PROJECT_MANAGER` directly in the service layer.
4. Denied requests return `403 Forbidden`; requests for resources the user cannot even see return `404 Not Found`.

## Local Setup

```bash
cp .env.example .env
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m app.db.seed
alembic upgrade head
uvicorn app.main:app --reload
```

- REST API docs: `http://127.0.0.1:8000/api/v1/docs`
- Web app: `http://127.0.0.1:8000/login`

## Branch History

Each feature was developed on its own branch, verified end-to-end via
Postman (API) and manual browser testing (web), then merged into `main`.
See individual branch READMEs for step-by-step implementation notes.

## Roadmap Status

✅ Auth · RBAC · Users · Organizations · Teams · Projects · Tasks ·
Comments/Attachments · Notifications/Activity Logs · Search/Filter/
Pagination · Middleware · Global Exception Handling · Web Frontend (Jinja2)


