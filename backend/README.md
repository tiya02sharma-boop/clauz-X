# Clauz X backend

Run from the repository root after installing dependencies:

```sh
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python -m backend.app  # http://127.0.0.1:5001
python -m backend.monitor --once
python -m unittest discover -s backend/tests -v
```

Set `GEMINI_API_KEY` for live structured Gemini calls. `DEMO_MODE=true` permits a plainly-labelled simulated *candidate* only when Gemini extraction fails; it never writes a live rule. A curated registry of official central sources is in `backend/data/sources.json`; every entry is deliberately inactive initially. Review each source and set only the sources you want to monitor to `"active": true`.

Endpoints: `POST /api/applicability/check`, `POST /admin/monitor/run`, `GET /admin/monitor/status`, `GET /admin/sources`, `GET /admin/review-queue`, `GET /admin/review-queue/<id>`, `POST /admin/approve/<id>`, and `POST /admin/reject/<id>`.

## Deadlines, Calendar & WhatsApp Reminders

Clauz X provides an automated, one-way compliance deadline calendar and WhatsApp notification backend:

- **Due-date calculation engine** (`backend/due_date_parser.py`): Parses standard `"Nth of following month"` patterns for monthly and quarterly obligations. Follows a strict zero-guessing policy for irregular/one-time rules (`needs_manual_date_entry: true`).
- **Idempotent reminder scheduler** (`backend/reminder_scheduler.py`): Automatically triggers notifications 7, 3, and 1 days before due dates. Checks append-only logs (`backend/data/reminder_logs.json`) to guarantee zero duplicate messages even if re-triggered on the same date.
- **WhatsApp provider layer** (`backend/whatsapp_sender.py`): Integrates with Twilio with strict TLS verification. Automatically falls back to simulation mode with `status: "simulated"` when credentials are absent, and maps provider error codes to stable application codes (`INVALID_NUMBER`, `RECIPIENT_NOT_OPTED_IN`, `TEMPLATE_REQUIRED`, `WHATSAPP_SEND_FAILED`).
- **Endpoints**:
  - `POST /api/compliance/businesses` — Register or update MSME profile and compute live obligation calendar.
  - `GET /api/compliance/businesses` — List registered businesses.
  - `GET /api/compliance/businesses/<business_id>/calendar` — Retrieve computed calendar for an `as_of` date.
  - `POST /api/compliance/reminders/run` — Manual or cron trigger for the reminder cycle (`{"as_of_date": "YYYY-MM-DD"}`).
  - `GET /api/compliance/reminders/log` — Admin & ops log viewer for reminder dispatch history.

Some regulator sites deny automated requests or have certificate-chain issues. The monitor reports these explicitly as `SOURCE_ACCESS_DENIED` or `TLS_VERIFICATION_FAILED`; it deliberately never bypasses source access controls or disables TLS verification. Configure an official API, RSS, or download feed when a listing page blocks automation.

## Product operating model

Clauz X ships a release-managed baseline in `data/baseline_rules.json`; startup installs it into `rules.json` only when the live table is empty. Internal regulatory operations—not customers or CAs—prepare and approve source-backed baseline releases and amendments. Send official email alerts, permitted regulator feeds, or licensed-provider events to `POST /admin/regulatory-updates`; they are held for internal triage and never alter a rule automatically. Internal operations can create a draft using `POST /internal/rules/drafts`.
