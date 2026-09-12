# Clauz X

A compliance assistant for Indian businesses. Enter your business profile — it maps applicable legal obligations, builds a deadline calendar, and sends reminders.

## How it works

```
Business profile (entity type, state, sector, GST status, etc.)
        ↓
Applicability engine matches approved compliance rules
        ↓
Obligations + deadlines are calculated and shown on a calendar
        ↓
WhatsApp reminders sent for upcoming due dates
        ↓
"Ask Clauz X" answers compliance questions from reviewed legal text
```

## Contract Health Report

The dashboard's **Contract Health Report** accepts one PDF contract and runs a
first-pass India-focused review. It checks the eight core templates
(indemnity, liability cap, termination, confidentiality, governing law, data
protection, IP and force majeure) plus parties/signing authority, scope and
GST/TDS, warranties, assignment/subcontracting, notices, and anti-bribery.

Each check is shown as **Compliant**, **Needs review**, or **Missing / high
risk**, with matching text where available. The initial checks are
deterministic keyword signals so the feature works without an AI key. They are
a starting playbook, not legal advice or automatic contract approval; have
Indian counsel tailor and approve the templates before production use.

API endpoints:

```text
POST /api/contracts/health         # JSON: contract_text, optional filename
POST /api/contracts/health/upload  # multipart form: contract=<PDF>
```

Regulatory changes go through a human review queue before updating the live rule table — nothing unreviewed affects your obligations automatically.

## Quick Start

**Frontend**
```bash
npm install
npm run dev        # http://localhost:5173
```

**Backend**
```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m backend.app   # http://localhost:5001
```

The deployed frontend calls the Render backend at
`https://clauzx-backend.onrender.com`. If you deploy the backend under a
different Render URL, set Netlify's `VITE_BACKEND_URL` environment variable to
that exact URL and redeploy the frontend. Verify the deployment with
`GET /api/health` before using the applicability dashboard.

## Configuration

Create `backend/.env` (optional):

```env
GEMINI_API_KEY=your_key_here
WASENDER_API_KEY=your_whatsapp_key
```

## Regulatory monitoring

`POST /admin/monitor/run` checks configured official sources, detects changed
notices, and uses Gemini to create source-backed applicability-rule drafts from
linked PDFs or notice text. Drafts enter the review queue; only
`POST /admin/approve/<candidate_id>` writes a rule to the live catalog.

To run periodic checks from one always-on backend instance, set
`ENABLE_REGULATORY_MONITOR=true` and `MONITOR_INTERVAL_MINUTES=360`. For a
multi-instance deployment, run `python -m backend.monitor --once` from the
hosting platform scheduler instead.
