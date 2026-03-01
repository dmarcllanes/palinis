from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse
from config import ADMIN_PASSWORD
from admin.auth import require_admin
from repositories.db import get_pool
from repositories import booking_repo
from services.status_transition_service import validate_transition
from domain.enums import BookingStatus
from uuid import UUID

ADMIN_CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f1f5f9; }

/* ── Topbar ── */
.admin-topbar { background: var(--primary, #0f3f5e); color: #fff; padding: 0 2rem; height: 56px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; }
.admin-brand { font-weight: 700; font-size: 1rem; letter-spacing: 0.01em; }
.admin-brand span { color: #7dd3fc; }
.topbar-right { display: flex; align-items: center; gap: 1.5rem; font-size: 0.85rem; }
.topbar-right a { color: #cbd5e1; text-decoration: none; }
.topbar-right a:hover { color: #fff; }
.logout-btn { background: #ef4444; color: #fff !important; padding: 0.35rem 0.85rem; border-radius: 9999px; font-weight: 600; border: none; cursor: pointer; }
.logout-btn:hover { background: #dc2626 !important; }

/* ── Layout ── */
.admin-body { padding: 2rem; max-width: 1200px; margin: 0 auto; }

/* ── Stats ── */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: #fff; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.stat-card .stat-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-light, #64748b); font-weight: 600; margin-bottom: 0.35rem; }
.stat-card .stat-num { font-size: 2rem; font-weight: 800; color: var(--primary, #0f3f5e); }
.stat-card.s-pending .stat-num  { color: #d97706; }
.stat-card.s-confirmed .stat-num { color: #2563eb; }
.stat-card.s-assigned .stat-num  { color: #7c3aed; }
.stat-card.s-completed .stat-num { color: #16a34a; }
.stat-card.s-cancelled .stat-num { color: #dc2626; }

/* ── Filter tabs ── */
.filter-tabs { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.tab-btn { padding: 0.45rem 1rem; border-radius: 20px; border: 1.5px solid var(--border, #e2e8f0); background: #fff; font-size: 0.82rem; font-weight: 600; color: var(--text-light, #64748b); cursor: pointer; text-decoration: none; transition: all 0.2s; }
.tab-btn:hover { border-color: var(--primary, #0f3f5e); color: var(--primary, #0f3f5e); }
.tab-btn.active { background: var(--primary, #0f3f5e); border-color: var(--primary, #0f3f5e); color: #fff; }

/* ── Table ── */
.table-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); overflow: hidden; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
thead th { background: #f8fafc; padding: 0.75rem 1rem; text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; font-weight: 600; border-bottom: 1.5px solid #e2e8f0; white-space: nowrap; }
tbody td { padding: 0.85rem 1rem; border-bottom: 1px solid #f1f5f9; color: #0f2d40; vertical-align: middle; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: #f8fafc; }
.no-data { text-align: center; padding: 3rem; color: #94a3b8; font-size: 0.95rem; }

/* ── Status badge ── */
.badge { display: inline-block; padding: 0.25rem 0.65rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
.badge-pending_payment  { background: #fef9c3; color: #854d0e; }
.badge-confirmed        { background: #dbeafe; color: #1e40af; }
.badge-assigned         { background: #ede9fe; color: #6d28d9; }
.badge-in_progress      { background: #d1fae5; color: #065f46; }
.badge-completed        { background: #dcfce7; color: #166534; }
.badge-cancelled        { background: #fee2e2; color: #991b1b; }
.badge-flagged_for_review { background: #fef3c7; color: #92400e; }

/* ── Status form ── */
.status-form { display: flex; gap: 0.4rem; align-items: center; }
.status-select { padding: 0.3rem 0.5rem; border: 1.5px solid var(--border, #e2e8f0); border-radius: 6px; font-size: 0.78rem; color: var(--text-dark, #0f172a); background: #fff; }
.status-select:focus { outline: none; border-color: var(--primary, #0f3f5e); }
.status-submit { padding: 0.3rem 0.65rem; background: var(--primary, #0f3f5e); color: #fff; border: none; border-radius: 9999px; font-size: 0.78rem; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
.status-submit:hover { background: var(--primary-light, #1e628f); }

/* ── Flash ── */
.flash-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; padding: 0.75rem 1.25rem; border-radius: 10px; margin-bottom: 1.25rem; font-size: 0.88rem; font-weight: 500; }
.flash-error   { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; padding: 0.75rem 1.25rem; border-radius: 10px; margin-bottom: 1.25rem; font-size: 0.88rem; font-weight: 500; }

/* ── Login ── */
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f1f5f9; }
.login-card { background: #fff; border-radius: 16px; padding: 2.5rem; width: 100%; max-width: 380px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.login-logo { font-size: 1.1rem; font-weight: 800; color: var(--text-dark, #0f172a); margin-bottom: 0.25rem; }
.login-logo span { color: var(--primary, #0f3f5e); }
.login-card h2 { font-size: 1.25rem; color: var(--text-dark, #0f172a); margin: 0 0 1.75rem; font-weight: 700; }
.login-field { margin-bottom: 1rem; }
.login-field label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-dark, #0f172a); margin-bottom: 0.35rem; }
.login-field input { width: 100%; padding: 0.8rem 1rem; border: 2px solid var(--border, #e2e8f0); border-radius: 10px; font-size: 0.95rem; color: var(--text-dark, #0f172a); }
.login-field input:focus { outline: none; border-color: var(--primary, #0f3f5e); }
.login-btn { width: 100%; background: var(--primary, #0f3f5e); color: #fff; border: none; padding: 0.85rem; border-radius: 9999px; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 0.5rem; transition: background 0.2s; }
.login-btn:hover { background: var(--primary-light, #1e628f); }
.login-error { background: #fee2e2; color: #991b1b; padding: 0.7rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; }

@media (max-width: 640px) {
    .admin-body { padding: 1rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .topbar-right .topbar-label { display: none; }
}
"""

STATUS_LABELS = {
    "pending_payment":    "New Booking",
    "confirmed":          "Confirmed",
    "in_progress":        "Currently Working",
    "completed":          "Completed",
    "cancelled":          "Cancelled",
    "flagged_for_review": "Flagged",
}

ALLOWED_NEXT = {
    "pending_payment":    ["confirmed", "cancelled", "flagged_for_review"],
    "confirmed":          ["in_progress", "cancelled", "flagged_for_review"],
    "in_progress":        ["completed", "cancelled", "flagged_for_review"],
    "completed":          [],
    "cancelled":          [],
    "flagged_for_review": ["confirmed", "cancelled"],
}


def _topbar():
    return Div(
        Span(Span("Harbour Clean", cls=""), Span(" · Admin", cls=""), cls="admin-brand"),
        Div(
            Span("Admin Panel", cls="topbar-label"),
            A("← View Site", href="/"),
            Form(Button("Logout", cls="logout-btn"), method="POST", action="/admin/logout", hx_boost="false"),
            cls="topbar-right",
        ),
        cls="admin-topbar",
    )


def _status_badge(status: str):
    label = STATUS_LABELS.get(status, status)
    return Span(label, cls=f"badge badge-{status}")


def _status_form(booking_id, current_status: str):
    options = ALLOWED_NEXT.get(current_status, [])
    if not options:
        return Span("—", style="color:#94a3b8; font-size:0.8rem;")
    return Form(
        Select(
            *[Option(STATUS_LABELS.get(s, s), value=s) for s in options],
            cls="status-select", name="new_status",
        ),
        Button("Update", type="submit", cls="status-submit"),
        method="POST",
        action=f"/admin/bookings/{booking_id}/status",
        cls="status-form",
        hx_boost="false",
    )


def admin_login_page(error: str = ""):
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Admin Login – Harbour Clean Co."),
            Style(ADMIN_CSS),
        ),
        Body(
            Div(
                Div(
                    P("Harbour Clean", cls="login-logo"),
                    H2("Admin Login"),
                    Div(error, cls="login-error") if error else None,
                    Form(
                        Div(
                            Label("Password", fr="password"),
                            Input(type="password", id="password", name="password",
                                  placeholder="Enter admin password", autofocus=True),
                            cls="login-field",
                        ),
                        Button("Sign In", type="submit", cls="login-btn"),
                        method="POST",
                        action="/admin/login",
                    ),
                    cls="login-card",
                ),
                cls="login-page",
            ),
        ),
        lang="en",
    )


def admin_dashboard_page(bookings, status_filter=None, flash=None, flash_type="success"):
    counts = {}
    for s in ["pending_payment", "confirmed", "in_progress", "completed", "cancelled"]:
        counts[s] = sum(1 for b in bookings if b.status.value == s)
    total = len(bookings)

    flash_div = None
    if flash:
        flash_div = Div(flash, cls=f"flash-{flash_type}")

    tabs = [("all", "All", total)] + [
        ("pending_payment", "New",              counts["pending_payment"]),
        ("confirmed",       "Confirmed",        counts["confirmed"]),
        ("in_progress",     "Currently Working", counts["in_progress"]),
        ("completed",       "Completed",        counts["completed"]),
        ("cancelled",       "Cancelled",        counts["cancelled"]),
    ]

    rows = []
    for b in bookings:
        svc = b.service_type.value.replace("_", " ").title()
        rows.append(
            Tr(
                Td(str(b.id)[:8] + "…", style="font-family:monospace; color:#64748b; font-size:0.78rem;"),
                Td(b.customer_name),
                Td(b.email, style="color:#64748b;"),
                Td(svc),
                Td(str(b.service_date)),
                Td(f"{b.bedrooms}b / {b.bathrooms}ba", style="color:#64748b;"),
                Td(f"${b.total_price}", style="font-weight:700; color:#1a4d6d;"),
                Td(_status_badge(b.status.value)),
                Td(_status_form(b.id, b.status.value)),
            )
        )

    table = (
        Table(
            Thead(Tr(
                Th("ID"), Th("Customer"), Th("Email"), Th("Service"),
                Th("Date"), Th("Size"), Th("Price"), Th("Status"), Th("Action"),
            )),
            Tbody(*rows) if rows else Tbody(Tr(Td("No bookings found.", cls="no-data", colspan="9"))),
        )
    )

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Meta(http_equiv="Cache-Control", content="no-store, no-cache, must-revalidate"),
            Meta(http_equiv="Pragma", content="no-cache"),
            Title("Admin Dashboard – Harbour Clean Co."),
            Style(ADMIN_CSS),
        ),
        Body(
            _topbar(),
            Div(
                H2("Dashboard", style="font-size:1.3rem; font-weight:700; color:#0f2d40; margin:0 0 1.5rem;"),
                flash_div,

                # Stats
                Div(
                    Div(Div("Total", cls="stat-label"), Div(str(total), cls="stat-num"), cls="stat-card"),
                    Div(Div("New", cls="stat-label"), Div(str(counts["pending_payment"]), cls="stat-num"), cls="stat-card s-pending"),
                    Div(Div("Confirmed", cls="stat-label"), Div(str(counts["confirmed"]), cls="stat-num"), cls="stat-card s-confirmed"),
                    Div(Div("Working", cls="stat-label"), Div(str(counts["in_progress"]), cls="stat-num"), cls="stat-card s-assigned"),
                    Div(Div("Completed", cls="stat-label"), Div(str(counts["completed"]), cls="stat-num"), cls="stat-card s-completed"),
                    Div(Div("Cancelled", cls="stat-label"), Div(str(counts["cancelled"]), cls="stat-num"), cls="stat-card s-cancelled"),
                    cls="stats-grid",
                ),

                # Filter tabs
                Div(
                    *[A(f"{label} ({count})",
                        href=f"/admin?status={val}" if val != "all" else "/admin",
                        cls="tab-btn active" if (status_filter or "all") == val else "tab-btn")
                      for val, label, count in tabs],
                    cls="filter-tabs",
                ),

                # Table
                Div(Div(table, cls="table-wrap"), cls="table-card"),
                cls="admin-body",
            ),
        ),
        lang="en",
    )


# ── Route handlers ──

async def get_admin_login(request: Request):
    if request.session.get("admin"):
        return RedirectResponse("/admin", status_code=303)
    return admin_login_page()


async def post_admin_login(request: Request):
    form = await request.form()
    password = form.get("password", "")
    if password == ADMIN_PASSWORD:
        request.session["admin"] = True
        return RedirectResponse("/admin", status_code=303)
    return admin_login_page(error="Incorrect password. Try again.")


async def get_admin_dashboard(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    status = request.query_params.get("status")
    flash = request.session.pop("flash", None)
    flash_type = request.session.pop("flash_type", "success")
    bookings = await booking_repo.get_all(pool, status=status)
    return admin_dashboard_page(bookings, status_filter=status, flash=flash, flash_type=flash_type)


async def post_update_status(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    booking_id = UUID(request.path_params["id"])
    form = await request.form()
    new_status = form.get("new_status", "")
    try:
        booking = await booking_repo.get_by_id(pool, booking_id)
        if not booking:
            raise ValueError("Booking not found.")
        if booking.status.value == new_status:
            # Already in this state — silently ignore (e.g. back-button resubmit)
            return RedirectResponse("/admin", status_code=303)
        validate_transition(booking.status, BookingStatus(new_status))
        await booking_repo.update_status(pool, booking_id, new_status)
        request.session["flash"] = f"Booking updated to '{new_status.replace('_', ' ')}'."
        request.session["flash_type"] = "success"
    except ValueError as e:
        request.session["flash"] = str(e)
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin", status_code=303)


async def post_admin_logout(request: Request):
    request.session.clear()
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("session")
    return response
