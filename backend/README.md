# Clauz X backend

Run from the repository root after installing dependencies:

```sh
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python -m backend.app  # http://127.0.0.1:5001
python -m backend.monitor --once
python -m unittest discover -s backend/tests -v
```

Endpoints: `POST /api/applicability/check`, `POST /admin/monitor/run`, `GET /admin/monitor/status`, `GET /admin/sources`, `GET /admin/review-queue`, `GET /admin/review-queue/<id>`, `POST /admin/approve/<id>`, and `POST /admin/reject/<id>`.

## User Flow

```
1. Register business profile
   POST /api/compliance/businesses
   (entity type, state, sector, GST status, turnover, headcount)
        ↓
2. Engine maps profile → applicable compliance rules
   GET /api/compliance/businesses/<id>/calendar
   Returns obligations with calculated due dates
        ↓
3. User views compliance calendar in the frontend
   Upcoming deadlines are listed with filing details
        ↓
4. Reminders are dispatched automatically
   POST /api/compliance/reminders/run  (cron or manual)
   WhatsApp alerts sent 7, 3, and 1 day before each due date
        ↓
5. User asks compliance questions
   POST /api/ask
   Answers are grounded in reviewed legal text (Gemini optional)
        ↓
6. (Admin) Regulatory changes are monitored and queued
   POST /admin/monitor/run  →  GET /admin/review-queue
   Internal team approves/rejects before rules go live
```

## Deadlines, Calendar & WhatsApp Reminders

Clauz X provides an automated, one-way compliance deadline calendar and WhatsApp notification backend:

- **Due-date calculation engine** (`backend/due_date_parser.py`): Parses standard `"Nth of following month"` patterns for monthly and quarterly obligations. Follows a strict zero-guessing policy for irregular/one-time rules (`needs_manual_date_entry: true`).
- **Idempotent reminder scheduler** (`backend/reminder_scheduler.py`): Automatically triggers notifications 7, 3, and 1 days before due dates. Checks append-only logs (`backend/data/reminder_logs.json`) to guarantee zero duplicate messages even if re-triggered on the same date.
- **WhatsApp provider layer** (`backend/whatsapp_sender.py`): Integrates with Wasenderapi (www.wasenderapi.com).
- **Endpoints**:
  - `POST /api/compliance/businesses` — Register or update MSME profile and compute live obligation calendar.
  - `GET /api/compliance/businesses` — List registered businesses.
  - `GET /api/compliance/businesses/<business_id>/calendar` — Retrieve computed calendar for an `as_of` date.
  - `POST /api/compliance/reminders/run` — Manual or cron trigger for the reminder cycle (`{"as_of_date": "YYYY-MM-DD"}`).
  - `GET /api/compliance/reminders/log` — Admin & ops log viewer for reminder dispatch history.


