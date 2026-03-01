from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse
from config import ADMIN_PASSWORD
from admin.auth import require_admin
from repositories.db import get_pool
from repositories import booking_repo, cleaner_repo
from services import booking_service
from components.admin_ui import ADMIN_CSS, STATUS_LABELS, ALLOWED_NEXT
from domain.enums import BookingStatus
from uuid import UUID

ASSIGN_CSS = """
.assign-form { display: flex; gap: 0.35rem; align-items: center; }
.assign-select { padding: 0.28rem 0.5rem; border: 1.5px solid #c7d2fe; border-radius: 6px; font-size: 0.75rem; color: #0f172a; background: #fff; max-width: 140px; }
.assign-select:focus { outline: none; border-color: #6366f1; }
.assign-btn { padding: 0.28rem 0.6rem; background: #6366f1; color: #fff; border: none; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
.assign-btn:hover { background: #4f46e5; }
.assigned-name { font-size: 0.8rem; color: #4f46e5; font-weight: 600; }
.unassigned-note { font-size: 0.75rem; color: #94a3b8; font-style: italic; }
"""


def _topbar(active: str = "bookings"):
    def _link(label, href, key):
        cls = "topbar-nav-link active" if active == key else "topbar-nav-link"
        return A(label, href=href, cls=cls)

    return Div(
        A(
            Img(src='/images/logo.png', alt='Logo', style='height: 24px;'),
            "Filo Cleaning Services",
            Span("· Admin", cls="admin-brand-sub"),
            cls="admin-brand",
            href="/admin",
            style="display: flex; align-items: center; gap: 0.5rem; text-decoration: none;"
        ),
        Div(
            _link("Bookings", "/admin", "bookings"),
            _link("Cleaners", "/admin/cleaners", "cleaners"),
            Div(cls="topbar-divider"),
            A("View Site", href="/", cls="topbar-site-link"),
            Form(Button("Logout", cls="logout-btn"), method="POST", action="/admin/logout", hx_boost="false"),
            cls="topbar-right",
        ),
        cls="admin-topbar",
    )


def _status_badge(status: str):
    label = STATUS_LABELS.get(status, status)
    return Span(label, cls=f"badge badge-{status}")


def _status_form(booking_id, current_status: str):
    # When a booking is "assigned", only show manual overrides (not re-assign via status)
    options = [s for s in ALLOWED_NEXT.get(current_status, []) if s != "assigned"]
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


def _assign_cell(booking, cleaners: list, cleaner_map: dict):
    """
    For confirmed/assigned bookings: show assign dropdown.
    For others: show the assigned cleaner name if any.
    """
    assignable = {BookingStatus.confirmed, BookingStatus.assigned}

    if booking.status in assignable:
        return Form(
            Select(
                Option("— Select cleaner —", value="", disabled=True, selected=not booking.cleaner_id),
                *[Option(c.name, value=str(c.id), selected=(booking.cleaner_id == c.id))
                  for c in cleaners],
                cls="assign-select", name="cleaner_id", required=True,
            ),
            Button("Assign", type="submit", cls="assign-btn"),
            method="POST",
            action=f"/admin/bookings/{booking.id}/assign",
            cls="assign-form",
            hx_boost="false",
        )

    if booking.cleaner_id and booking.cleaner_id in cleaner_map:
        return Span(cleaner_map[booking.cleaner_id], cls="assigned-name")

    return Span("—", cls="unassigned-note")


def admin_login_page(error: str = ""):
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Admin Login – Filo Cleaning Services"),
            Style(ADMIN_CSS),
        ),
        Body(
            Div(
                Div(
                    Img(src='/images/logo.png', alt='Filo Logo', style='height: 80px; margin: 0 auto 1rem; display: block;'),
                    P("Filo Cleaning Services", cls="login-logo", style="margin-bottom: 0.25rem; text-align: center;"),
                    H2("Admin Login", style="margin-top: 0; text-align: center;"),
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


def admin_dashboard_page(bookings, active_cleaners, status_filter=None, flash=None, flash_type="success"):
    stat_keys = ["pending_confirmation", "confirmed", "assigned", "in_progress", "completed", "cancelled"]
    counts = {s: sum(1 for b in bookings if b.status.value == s) for s in stat_keys}
    total = len(bookings)

    flash_div = Div(flash, cls=f"flash-{flash_type}") if flash else None

    # Build cleaner lookup: UUID → name
    cleaner_map = {c.id: c.name for c in active_cleaners}

    tabs = [("all", "All", total)] + [
        ("pending_confirmation", "New",    counts["pending_confirmation"]),
        ("confirmed",       "Confirmed",  counts["confirmed"]),
        ("assigned",        "Assigned",   counts["assigned"]),
        ("in_progress",     "In Progress", counts["in_progress"]),
        ("completed",       "Completed",  counts["completed"]),
        ("cancelled",       "Cancelled",  counts["cancelled"]),
    ]

    rows = [
        Tr(
            Td(str(b.id)[:8] + "…", style="font-family:monospace; color:#64748b; font-size:0.78rem;"),
            Td(b.customer_name),
            Td(b.email, style="color:#64748b;"),
            Td(b.service_type.value.replace("_", " ").title()),
            Td(str(b.service_date)),
            Td(f"{b.bedrooms}b / {b.bathrooms}ba", style="color:#64748b;"),
            Td(f"${b.total_price}", style="font-weight:700; color:#1a4d6d;"),
            Td(_status_badge(b.status.value)),
            Td(_assign_cell(b, active_cleaners, cleaner_map)),
            Td(_status_form(b.id, b.status.value)),
        )
        for b in bookings
    ]

    table = Table(
        Thead(Tr(
            Th("ID"), Th("Customer"), Th("Email"), Th("Service"),
            Th("Date"), Th("Size"), Th("Price"), Th("Status"),
            Th("Cleaner"), Th("Action"),
        )),
        Tbody(*rows) if rows else Tbody(Tr(Td("No bookings found.", cls="no-data", colspan="10"))),
    )

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Meta(http_equiv="Cache-Control", content="no-store, no-cache, must-revalidate"),
            Meta(http_equiv="Pragma", content="no-cache"),
            Title("Admin Dashboard – Filo Cleaning Services"),
            Style(ADMIN_CSS + ASSIGN_CSS),
        ),
        Body(
            _topbar(active="bookings"),
            Div(
                H2("Dashboard", style="font-size:1.3rem; font-weight:700; color:#0f2d40; margin:0 0 1.5rem;"),
                flash_div,
                Div(
                    Div(Div("Total",     cls="stat-label"), Div(str(total),                    cls="stat-num"), cls="stat-card"),
                    Div(Div("New",       cls="stat-label"), Div(str(counts["pending_confirmation"]), cls="stat-num"), cls="stat-card s-pending"),
                    Div(Div("Confirmed", cls="stat-label"), Div(str(counts["confirmed"]),       cls="stat-num"), cls="stat-card s-confirmed"),
                    Div(Div("Assigned",  cls="stat-label"), Div(str(counts["assigned"]),        cls="stat-num"), cls="stat-card s-assigned"),
                    Div(Div("Completed", cls="stat-label"), Div(str(counts["completed"]),       cls="stat-num"), cls="stat-card s-completed"),
                    Div(Div("Cancelled", cls="stat-label"), Div(str(counts["cancelled"]),       cls="stat-num"), cls="stat-card s-cancelled"),
                    cls="stats-grid",
                ),
                Div(
                    *[A(f"{label} ({count})",
                        href=f"/admin?status={val}" if val != "all" else "/admin",
                        cls="tab-btn active" if (status_filter or "all") == val else "tab-btn")
                      for val, label, count in tabs],
                    cls="filter-tabs",
                ),
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
    all_cleaners = await cleaner_repo.get_all(pool)
    active_cleaners = [c for c in all_cleaners if c.is_active]
    return admin_dashboard_page(
        bookings, active_cleaners,
        status_filter=status, flash=flash, flash_type=flash_type,
    )


async def post_update_status(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    booking_id = UUID(request.path_params["id"])
    form = await request.form()
    new_status = form.get("new_status", "")
    try:
        updated = await booking_service.update_booking_status(pool, booking_id, new_status)
        label = STATUS_LABELS.get(updated.status.value, updated.status.value)
        request.session["flash"] = f"Booking updated to '{label}'."
        request.session["flash_type"] = "success"
    except ValueError as e:
        request.session["flash"] = str(e)
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin", status_code=303)


async def post_assign_cleaner(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    booking_id = UUID(request.path_params["id"])
    form = await request.form()
    cleaner_id_str = form.get("cleaner_id", "")
    try:
        cleaner_id = UUID(cleaner_id_str)
        booking = await booking_service.assign_cleaner_to_booking(pool, booking_id, cleaner_id)
        cleaner = await cleaner_repo.get_by_id(pool, cleaner_id)
        cleaner_name = cleaner.name if cleaner else "Cleaner"
        request.session["flash"] = f"'{cleaner_name}' assigned to booking #{str(booking.id)[:8]}."
        request.session["flash_type"] = "success"
    except (ValueError, Exception) as e:
        request.session["flash"] = str(e)
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin", status_code=303)


async def post_admin_logout(request: Request):
    request.session.clear()
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("session")
    return response
