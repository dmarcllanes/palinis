# Harbour Clean Co – System Architecture

## Overview

Harbour Clean Co is a Sydney-based home cleaning booking platform.

This system is built using:

- FastHTML (server-rendered web framework)
- Supabase (Postgres database only)
- Pydantic v2 (domain and validation layer)
- Service-layer architecture
- Direct Postgres connection (no Supabase REST client)

Stripe is not integrated at this stage.

This platform must assume that some users may submit malicious, fraudulent, spam, or abusive bookings.
The system must enforce validation, abuse detection, and controlled state transitions.

---

## Architecture Philosophy

The system follows strict layer separation:

Routes Layer
↓
Service Layer
↓
Domain Layer (Pydantic models)
↓
Repository Layer (SQL queries)
↓
Supabase Postgres

Rules:

- Routes MUST NOT contain business logic.
- Routes MUST NOT access database directly.
- All data entering system MUST be validated using Pydantic.
- State transitions must be enforced in service layer.
- Pricing logic must be pure and stateless.
- Sydney service area validation must query DB (not hardcoded).
- Abuse detection must occur before persistence where possible.

---

## Core Domain Concepts

### Booking Status State Machine

Allowed transitions:

pending_confirmation → confirmed
confirmed → assigned
assigned → in_progress
in_progress → completed
assigned → completed
any → cancelled
any → flagged_for_review
flagged_for_review → confirmed
flagged_for_review → cancelled

Invalid transitions must raise errors.

State transitions must be validated in `status_transition_service`.

**Initial status on booking creation: `pending_confirmation`**
A booking is only confirmed after admin manually approves it.
`pending_payment` is no longer used — it has been renamed to `pending_confirmation`.

---

## Time Slot & Availability System

### Fixed Time Slots

Bookings require both a date and a time slot. Time slots are fixed in code (not DB):

- 8:00 AM
- 10:00 AM
- 12:00 PM
- 2:00 PM
- 4:00 PM

Defined in `services/availability_service.py` as `TIME_SLOTS`.

### Availability Rule

A slot is considered **unavailable** only when:

```
count of bookings at that date+time with status IN ('confirmed', 'assigned', 'completed')
>= count of active cleaners
```

`pending_confirmation` and `flagged_for_review` bookings do NOT block slots.
A slot only becomes unavailable after admin confirms a booking.

### Availability Endpoint

`GET /book/slots?date=YYYY-MM-DD` → returns JSON `{ "slots": ["08:00:00", ...] }`

Used by the booking wizard Step 3 to dynamically load available time slots after date selection.

### Alternative Suggestions

When a slot is full, `validate_slot()` raises `ValueError` with alternatives:
- Other open slots on the same day (if any)
- Or the next available date within 7 days with open slots

---

## Pricing Rules

Price is determined by:

- Service type (regular, deep, end_of_lease)
- Bedrooms
- Bathrooms
- Add-ons
- Frequency discount

Pricing logic must live inside `pricing_service`.

It must:
- Be deterministic
- Have no side effects
- Never trust raw route input

---

## Service Area Validation

Service areas are stored in `service_areas` table.

Booking is rejected if:
- postcode does not exist
- is_active is false

No postcode should be hardcoded.

---

## Booking Creation Flow

Order of operations in `booking_service.create_booking()`:

1. Validate postcode against `service_areas` DB table
2. Validate time slot availability (`availability_service.validate_slot`)
3. Calculate price server-side (`pricing_service`)
4. Persist booking to DB (status defaults to `pending_confirmation`)
5. Send confirmation email (stub)

---

## Abuse & Malicious Intent Protection

The system must assume that some users may attempt:

- Fake bookings
- Spam submissions
- Invalid contact details
- Repeated automated requests
- No-show abuse
- Intentional operational disruption

The architecture must enforce the following protections:

### 1. Input Validation (Required)

All booking inputs must:

- Be validated using strict Pydantic schemas
- Reject malformed emails
- Reject invalid phone formats
- Enforce numeric bounds on bedrooms/bathrooms
- Enforce enum-restricted service types

No raw dictionary should be inserted into the database.

---

### 2. Bot Protection

Booking routes must implement:

- CAPTCHA or equivalent human verification
- Rate limiting by IP
- Duplicate submission detection

The system must log IP address for abuse tracking.

---

### 3. Risk Scoring Layer

Before booking persistence, the system may compute a risk score based on:

- Disposable email domains
- Repeated IP submissions
- Suspicious phone format
- Inconsistent suburb/postcode
- Excessive booking frequency

If risk exceeds threshold:

Booking status must be set to:

flagged_for_review

Admin must manually approve before confirmation.

---

### 4. Contact Verification (Optional but Recommended)

Future implementation may include:

- SMS verification before confirmation
- Email confirmation link before activation

Bookings should not automatically move to confirmed without validation.

---

### 5. Rate Limiting Rules

System must:

- Limit booking attempts per IP
- Throttle repeated API calls
- Log suspicious activity

Repeated abuse may result in temporary IP block.

---

### 6. Admin Protection

Admin routes must:

- Require authentication
- Enforce role-based access
- Prevent direct status manipulation without transition validation

No direct DB status updates allowed from UI.

---

## Database Strategy

Supabase is used as raw Postgres.

Connection is established using DATABASE_URL.

No business logic should depend on Supabase client SDK.

DB must enforce:

- NOT NULL constraints
- ENUM constraints where possible
- Indexed columns on:
  - booking_date
  - postcode
  - status

Sensitive operations must be handled in backend only.

### Migrations

| File | Description |
|------|-------------|
| `001` | Create service_areas table |
| `002` | Create bookings table (status default: `pending_confirmation`) |
| `003` | Create cleaners table |
| `004` | Seed service areas |
| `005` | Update cleaners schema |
| `006` | Add cleaner_id to bookings |
| `007` | Add `service_time TIME` column to bookings |
| `008` | Rename status `pending_payment` → `pending_confirmation` |

---

## UI & Frontend

### Booking Wizard (5 steps)

1. **Service Type** — Regular / Deep / End of Lease
2. **Property Size** — Bedrooms + Bathrooms + live price preview
3. **Date & Time** — Date picker + dynamic time slot grid (fetched via `/book/slots`)
4. **Contact Details** — Name, email, phone, address, postcode
5. **Review & Confirm** — Summary of all fields before submission

Time slots are rendered as clickable cards. Unavailable slots shown greyed out with ✕.
`service_time` is submitted as a hidden form field (`HH:MM:SS` format).

### Navbar Design System

All non-marketing pages share a consistent modern navbar:

- White background, no floating/pill shape
- 3px gradient accent line at top (navy `#0f3f5e` → green `#1e9a68`)
- Subtle shadow `0 1px 12px rgba(15,63,94,0.07)`
- Brand dot (green circle) + "Harbour Clean Co." + grey sub-label
- Right-side links vary by page
- Mobile: sub-labels hidden, links compact

| Page | CSS class | Right links |
|------|-----------|-------------|
| Booking form | `.book-nav` | Track Booking · Home |
| Booking confirmation | `.book-nav` | Track Booking · Book Again |
| Booking lookup | `.book-nav` | Home · Book a Cleaning |
| Admin | `.admin-topbar` | Bookings · Cleaners · View Site · Logout |
| Cleaner portal | `.cl-topbar` | Sign Out |

The marketing homepage retains its own floating pill navbar (defined in `static/css/styles.css`).

---

## Security Rules

- All booking creation must pass domain validation.
- State transitions must be validated in service layer.
- Risk scoring must occur before booking confirmation.
- Suspicious bookings must be quarantined.
- System must be resilient against automated abuse.
- Admin credentials must never be hardcoded.

---

## Observability & Logging

The system must log:

- Booking creation attempts
- Failed validation attempts
- Flagged bookings
- Status transitions
- Suspicious IP patterns

Logs must not expose sensitive user data.

---

## Future Extensions

- Stripe payment integration
- SMS verification system
- Recurring billing engine
- AI-based scheduling
- Fraud detection scoring engine
- Multi-city expansion

Architecture must remain modular, layered, and service-driven.

Security and abuse prevention are first-class architectural concerns.
