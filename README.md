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

## Configuration

Create `backend/.env` (optional):

```env
GEMINI_API_KEY=your_key_here
WASENDER_API_KEY=your_whatsapp_key
```

