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

pending_payment → confirmed  
confirmed → assigned  
assigned → completed  
any → cancelled  
any → flagged_for_review  

Invalid transitions must raise errors.

State transitions must be validated in `status_transition_service`.

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
- Cleaner portal
- Recurring billing engine
- AI-based scheduling
- Fraud detection scoring engine
- Multi-city expansion

Architecture must remain modular, layered, and service-driven.

Security and abuse prevention are first-class architectural concerns.