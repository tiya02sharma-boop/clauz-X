# Clauz X — Regulatory Compliance Cockpit

Clauz X is a local-first compliance application for Indian businesses. It uses an approved, deterministic rule table to identify applicable obligations, calculate supported deadlines, present a compliance calendar, and send reminders.

The product combines a React frontend with a Flask API. It keeps a clear boundary between source monitoring, internal review, and the live obligation table.

## Features

- Business profile: entity type, state, sector, turnover, headcount, GST status, and filing scheme.
- Deterministic obligation mapping from approved rules.
- Applicable-obligations dashboard and compliance calendar.
- **Ask Clauz X**: source-grounded compliance Q&A from reviewed legal passages.
- Review-first document-drafting interface for routine documents.
- Regulatory-source monitoring, change candidates, review queue, and audit logs.
- Scheduled WhatsApp reminders when a provider is configured.

## Architecture

```text
React + Vite frontend (port 5173)
            |
            | HTTP / JSON
            v
Flask API (port 5001)
 ├─ Applicability engine       → approved rules + business profile
 ├─ Calendar / reminders       → calculated dates + delivery log
 ├─ Ask Clauz X                → reviewed legal corpus + optional Gemini
 ├─ Regulatory monitor         → configured official-source checks
 ├─ Review queue               → candidate changes awaiting approval
 └─ Local JSON data store      → rules, sources, audit trail, businesses
```

## Obligation-update flow

```text
Official notice, feed, or permitted source
        ↓
Monitoring detects a change
        ↓
Candidate update is stored in the review queue
        ↓
Internal review and source validation
        ↓
Approved rule is written to the live rule table
        ↓
Business calendars and obligations are recomputed
```

Unreviewed monitoring output and AI-generated candidates never automatically become live user obligations.

## Local setup

### Prerequisites

- Node.js 20+
- Python 3.11+

### Frontend

```bash
npm install
npm run dev
```

Open http://127.0.0.1:5173/.

### Backend

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m backend.app
```

The API runs at http://127.0.0.1:5001/. Set `VITE_BACKEND_URL` before starting Vite to use a different API address.

## GitHub Pages

Pushing to `main` publishes the static React frontend through GitHub Actions. In the
repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.
The Flask API requires a separate Python-capable host; configure its public URL as the
`VITE_BACKEND_URL` GitHub Actions repository variable before publishing if you want the
live dashboard to reach it.

## Core API routes

| Route | Purpose |
| --- | --- |
| `POST /api/applicability/check` | Evaluate approved rules for a business profile. |
| `POST /api/compliance/businesses` | Create or update a business and compute obligations. |
| `GET /api/compliance/businesses/<id>/calendar` | Return the business calendar. |
| `POST /api/ask` | Ask a grounded Indian-compliance question. |
| `POST /api/compliance/reminders/run` | Run the reminder scheduler. |
| `GET /admin/sources` | List configured regulatory sources. |
| `POST /admin/monitor/run` | Run a monitoring cycle. |
| `GET /admin/review-queue` | List proposed rule candidates. |
| `POST /admin/approve/<id>` | Approve a validated rule candidate. |
| `POST /admin/reject/<id>` | Reject a candidate. |

## Data files

Runtime data is held locally under `backend/data/`.

| File | Purpose |
| --- | --- |
| `baseline_rules.json` | Vetted product baseline. |
| `rules.json` | Live, approved rules evaluated by the application. |
| `legal_corpus.json` | Reviewed legal passages used for grounded answers. |
| `sources.json` | Configured regulatory sources. |
| `source_state.json` | Last-seen monitoring state. |
| `pending_review_queue.json` | Candidate regulatory changes pending review. |
| `businesses.json` | Saved business profiles and calculated obligations. |
| `reminder_logs.json` | Reminder-delivery audit log. |
| `audit_log.json` | Application audit events. |

## Optional configuration

Create `backend/.env` for optional integrations:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
WASENDER_API_KEY=your_whatsapp_provider_key
```

Without a Gemini key, Ask Clauz X returns retrieved reviewed material when available instead of inventing an answer. Without WhatsApp credentials, reminder delivery is not performed.

## Safety notes

- Clauz X prepares compliance information and drafts; it does not submit filings to GSTN, MCA, EPFO, ESIC, or government portals.
- Verify material facts, deadlines, and portal instructions before filing.
- Do not disable TLS verification or bypass access controls on regulator websites. Use official APIs, RSS feeds, downloadable notices, or licensed feeds where available.

## Verification

```bash
npm run build
.venv/bin/python -m unittest discover -s backend/tests -v
```
