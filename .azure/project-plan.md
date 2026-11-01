# NetCalc – IPv4 Subnetting and VLSM Calculator

**Status**: Planning
**Created**: 2026-11-01
**Mode**: Full-stack application

## 1. Overview

NetCalc is a college project that helps students and network administrators calculate IPv4 subnetting and Variable Length Subnet Masking (VLSM) plans. It provides a React web interface backed by a Flask REST API and SQLite persistence.

The application accepts an IPv4 network and subnetting requirements, validates the input, calculates network/broadcast addresses, usable host ranges, masks, and wildcard masks, and presents an ordered, copyable result. VLSM allocation assigns the largest requested host groups first and reports unallocated address space or invalid requirements clearly.

## 2. Goals & Scope

### Goals

- Make CIDR and traditional subnetting calculations understandable and error-resistant.
- Support equal-size subnetting and VLSM allocation for IPv4 networks.
- Explain results with binary/octet breakdowns suitable for classroom learning.
- Allow users to save, reopen, and delete calculation history.
- Keep calculation logic deterministic, testable, and independent of the UI.

### In scope

- IPv4/CIDR validation, subnet counts, host counts, ranges, and masks.
- VLSM requests by department/name and required host count.
- Calculation history stored in SQLite.
- Responsive accessible React UI and Flask JSON API.

### Out of scope

- IPv6, live network probing, DNS/IP ownership lookups, user accounts, and multi-tenant collaboration.
- Cloud deployment configuration beyond a deployment-ready application structure.

## 3. User Experience & Functional Requirements

1. A landing/calculator view provides tabs or modes for **Subnet Calculator** and **VLSM Calculator**.
2. The subnet form accepts a network address/CIDR and either a desired subnet count or host count, with an optional explanation toggle.
3. Results show summary values, a subnet table, usable ranges, and validation warnings; tables support copying individual values.
4. The VLSM form accepts a base network and a repeatable list of named host requirements. It sorts requirements by descending size, allocates aligned blocks, and displays allocation order and remaining space.
5. Invalid octets, non-contiguous masks, negative/zero requirements, duplicate names, and insufficient address space produce actionable inline errors without making an API request when detectable in the browser.
6. History lists saved calculations with type, input summary, timestamp, and delete/open actions. Saving is explicit and never stores secrets.
7. The UI is keyboard navigable, mobile responsive, uses semantic labels, and exposes calculation errors in an accessible live region.

## 4. Architecture

NetCalc uses a browser-to-API architecture:

- **React frontend** owns forms, client-side validation, result tables, history navigation, and presentation.
- **Flask backend** exposes JSON endpoints, validates all inputs again, invokes pure Python calculation services, and persists history.
- **SQLite** stores normalized calculation records and JSON input/result snapshots for reproducibility.

The backend is organized into routes/controllers, schemas/validation, calculation domain services, and repository/database modules. Calculation functions have no Flask or database dependencies. The frontend uses a small API client with a configurable `VITE_API_BASE_URL`.

## 5. Services & Data Stores

| Service | Technology | Responsibility |
|---|---|---|
| `frontend` | React, TypeScript, Vite | Calculator forms, accessible result visualization, history UI |
| `backend` | Python, Flask | REST API, validation, calculation orchestration, persistence |

**Data Stores**: SQLite

SQLite tables:

- `calculations`: id, calculation type, title, input JSON, result JSON, created_at.
- `vlsm_allocations` (optional normalized detail): calculation_id, label, requested_hosts, allocated_prefix, network_address, broadcast_address, first_host, last_host.

Use SQLite foreign keys, UTC timestamps, parameterized queries, and a migration/initialization script. No authentication or personal data is required.

## 6. Design System & UI

**Component Library**: Fluent UI v9
**Visual direction**: Clean academic network-tool interface with a navy/blue primary palette, high-contrast status colors, generous whitespace, and monospace styling for addresses and masks.
**Layout**: Responsive centered shell; desktop two-column form/results layout and mobile single-column flow.

Core components:

- App shell with navigation and project title.
- Mode tabs, labeled Fluent inputs, number inputs, and repeatable VLSM requirement rows.
- Primary/secondary action buttons, validation messages, loading indicator, empty states.
- Summary cards for network, mask, usable hosts, and subnet count.
- Fluent DataGrid-style subnet/VLSM result tables with sticky headers and copy actions.
- History drawer/page with confirmation for deletion.

The interface must not expose raw stack traces. Results should use semantic tables, visible focus states, and `aria-live` announcements for completion and errors.

## 7. API Contracts

Base path: `/api`

- `GET /api/health` → `{ "status": "ok" }`
- `POST /api/calculations/subnet`
  - Request: `{ "network": "192.168.10.0/24", "subnet_count": 4 | null, "hosts_per_subnet": 50 | null, "explain": true }`
  - Response: validated summary plus `subnets[]`, each containing prefix, mask, wildcard, network, first_host, last_host, broadcast, and usable_hosts.
- `POST /api/calculations/vlsm`
  - Request: `{ "network": "10.0.0.0/24", "requirements": [{ "name": "Admissions", "hosts": 60 }] }`
  - Response: base-network summary, ordered `allocations[]`, and remaining ranges.
- `POST /api/history` → persist a completed calculation and return its id.
- `GET /api/history` → paginated newest-first summaries.
- `GET /api/history/<id>` → complete saved input/result.
- `DELETE /api/history/<id>` → `{ "deleted": true }`.

All errors use `{ "error": { "code": "...", "message": "...", "fields": {} } }` with appropriate 4xx status codes. Enable CORS only for the configured local frontend origin.

## 8. Security, Configuration & Reliability

- Validate and canonicalize every address, prefix, host count, and list length on the server.
- Use parameterized SQLite statements and constrain request body sizes.
- Do not execute user input or interpolate it into SQL, HTML, shell commands, or log formats.
- Keep configuration in environment variables (`DATABASE_PATH`, `FRONTEND_ORIGIN`, `FLASK_ENV`); provide a non-secret `.env.example`.
- Return generic production errors and log server-side diagnostics without request contents that could contain sensitive data.
- Add health checks, graceful database initialization, and deterministic JSON serialization.

## 9. Testing & Acceptance Criteria

- Unit tests cover IPv4 parsing, CIDR/mask conversion, subnet counts, host capacity, alignment, boundary addresses, and VLSM first-fit allocation.
- API tests cover successful subnet/VLSM requests, malformed JSON, all validation errors, history CRUD, and health.
- Frontend tests cover form validation, loading/error states, result rendering, copy actions, and history flows.
- An end-to-end smoke test submits one subnet calculation and one VLSM calculation through the running frontend and confirms displayed results.
- Acceptance: no overlapping VLSM allocations; every allocation is aligned and within the base network; reserved network/broadcast addresses are excluded from usable counts; refresh preserves only explicitly saved history; keyboard and narrow-screen use remain functional.

## 10. Implementation & Delivery Plan

1. Scaffold the React/Vite frontend and Flask backend with shared environment documentation.
2. Implement pure IPv4/subnet/VLSM domain services and exhaustive unit tests.
3. Add SQLite schema, repository, history endpoints, and API validation.
4. Build Fluent UI calculator forms, result tables, explanations, and history screens.
5. Wire the API client, loading/error handling, and responsive accessibility behavior.
6. Run backend, frontend, integration, and smoke tests; document local setup and deployment commands.

