from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse
from admin.auth import require_admin
from admin.cleaner_auth import hash_password
from repositories.db import get_pool
from repositories import cleaner_repo
from components.admin_ui import ADMIN_CSS
from uuid import UUID

ADMIN_CLEANERS_CSS = """
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.section-header h2 { font-size: 1.3rem; font-weight: 700; color: #0f2d40; margin: 0; }
.section-header span { font-size: 0.85rem; color: #64748b; }

.add-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 2rem; }
.add-card h3 { font-size: 0.85rem; font-weight: 700; color: #0f2d40; margin: 0 0 1.25rem; text-transform: uppercase; letter-spacing: 0.06em; }
.add-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.85rem; margin-bottom: 1rem; }
.add-field { display: flex; flex-direction: column; gap: 0.3rem; }
.add-field label { font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.add-field input { padding: 0.65rem 0.9rem; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 0.88rem; color: #0f172a; }
.add-field input:focus { outline: none; border-color: #0f3f5e; }
.btn-add { background: #1e9a68; color: #fff; border: none; padding: 0.65rem 1.5rem; border-radius: 9999px; font-weight: 700; font-size: 0.88rem; cursor: pointer; }
.btn-add:hover { background: #15803d; }

.active-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 0.4rem; vertical-align: middle; }
.dot-active   { background: #22c55e; }
.dot-inactive { background: #cbd5e1; }

.action-cell { display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center; }
.toggle-form button { padding: 0.28rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; cursor: pointer; border: 1.5px solid; transition: all 0.2s; }
.btn-deactivate { background:#fff; border-color:#fca5a5; color:#dc2626; }
.btn-deactivate:hover { background:#fee2e2; }
.btn-activate   { background:#fff; border-color:#86efac; color:#16a34a; }
.btn-activate:hover { background:#dcfce7; }
.btn-del { background:#fff; border-color:#e2e8f0; color:#94a3b8; padding:0.28rem 0.65rem; border-radius:9999px; font-size:0.75rem; font-weight:600; cursor:pointer; border-width:1.5px; transition:all 0.2s; }
.btn-del:hover { border-color:#fca5a5; color:#dc2626; background:#fee2e2; }
"""


def _topbar():
    return Div(
        A(
            Img(src='/images/logo.png', alt='Logo', style='height: 24px; vertical-align: middle; margin-right: 0.5rem;'),
            Span("Filo Cleaning Services", cls=""), 
            Span(" · Admin", cls=""), 
            cls="admin-brand",
            href="/admin",
            style="display: flex; align-items: center; text-decoration: none;"
        ),
        Div(
            Span("Admin Panel", cls="topbar-label"),
            A("Bookings", href="/admin"),
            A("Cleaners", href="/admin/cleaners", style="color:#7dd3fc; font-weight:700;"),
            A("← View Site", href="/"),
            Form(Button("Logout", cls="logout-btn"), method="POST", action="/admin/logout", hx_boost="false"),
            cls="topbar-right",
        ),
        cls="admin-topbar",
    )


def admin_cleaners_page(cleaners, flash=None, flash_type="success"):
    flash_div = Div(flash, cls=f"flash-{flash_type}") if flash else None
    total = len(cleaners)
    active = sum(1 for c in cleaners if c.is_active)

    rows = []
    for c in cleaners:
        toggle_label = "Deactivate" if c.is_active else "Activate"
        toggle_cls = "btn-deactivate" if c.is_active else "btn-activate"
        new_active = "false" if c.is_active else "true"
        dot_cls = "dot-active" if c.is_active else "dot-inactive"

        rows.append(Tr(
            Td(str(c.id)[:8] + "…", style="font-family:monospace; color:#64748b; font-size:0.75rem;"),
            Td(c.name, style="font-weight:600;"),
            Td(c.email, style="color:#64748b;"),
            Td(c.phone or "—", style="color:#64748b;"),
            Td(c.username or "—", style="font-family:monospace; font-size:0.82rem;"),
            Td(Span(cls=f"active-dot {dot_cls}"), "Active" if c.is_active else "Inactive"),
            Td(
                Div(
                    Form(
                        Input(type="hidden", name="is_active", value=new_active),
                        Button(toggle_label, type="submit", cls=toggle_cls),
                        method="POST", action=f"/admin/cleaners/{c.id}/toggle",
                        cls="toggle-form", hx_boost="false",
                    ),
                    Form(
                        Button("Delete", type="submit", cls="btn-del",
                               onclick="return confirm('Delete this cleaner?')"),
                        method="POST", action=f"/admin/cleaners/{c.id}/delete",
                        cls="toggle-form", hx_boost="false",
                    ),
                    cls="action-cell",
                )
            ),
        ))

    table = Table(
        Thead(Tr(
            Th("ID"), Th("Name"), Th("Email"), Th("Phone"), Th("Username"), Th("Status"), Th("Actions"),
        )),
        Tbody(*rows) if rows else Tbody(
            Tr(Td("No cleaners yet. Add one below.", cls="no-data", colspan="7"))
        ),
    )

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Meta(http_equiv="Cache-Control", content="no-store, no-cache, must-revalidate"),
            Title("Cleaners – Admin · Filo Cleaning Services"),
            Style(ADMIN_CSS + ADMIN_CLEANERS_CSS),
        ),
        Body(
            _topbar(),
            Div(
                Div(
                    H2("Cleaners"),
                    Span(f"{total} total · {active} active"),
                    cls="section-header",
                ),
                flash_div,

                # Create cleaner form
                Div(
                    H3("Add New Cleaner"),
                    Form(
                        Div(
                            Div(Label("Full Name"),
                                Input(type="text", name="name", placeholder="Alex Johnson", required=True),
                                cls="add-field"),
                            Div(Label("Email"),
                                Input(type="email", name="email", placeholder="alex@example.com", required=True),
                                cls="add-field"),
                            Div(Label("Phone"),
                                Input(type="tel", name="phone", placeholder="04xx xxx xxx"),
                                cls="add-field"),
                            Div(Label("Username"),
                                Input(type="text", name="username", placeholder="alex.j", required=True,
                                      autocomplete="off"),
                                cls="add-field"),
                            Div(Label("Password"),
                                Input(type="password", name="password", placeholder="••••••••", required=True,
                                      autocomplete="new-password"),
                                cls="add-field"),
                            cls="add-grid",
                        ),
                        Button("+ Add Cleaner", type="submit", cls="btn-add"),
                        method="POST", action="/admin/cleaners/add", hx_boost="false",
                    ),
                    cls="add-card",
                ),

                Div(Div(table, cls="table-wrap"), cls="table-card"),
                cls="admin-body",
            ),
        ),
        lang="en",
    )


# ── Route handlers ──

async def get_admin_cleaners(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    flash = request.session.pop("flash", None)
    flash_type = request.session.pop("flash_type", "success")
    cleaners = await cleaner_repo.get_all(pool)
    return admin_cleaners_page(cleaners, flash=flash, flash_type=flash_type)


async def post_admin_add_cleaner(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    form = await request.form()
    name     = (form.get("name")     or "").strip()
    email    = (form.get("email")    or "").strip()
    phone    = (form.get("phone")    or "").strip()
    username = (form.get("username") or "").strip()
    password = (form.get("password") or "").strip()

    if not all([name, email, username, password]):
        request.session["flash"] = "Name, email, username and password are required."
        request.session["flash_type"] = "error"
        return RedirectResponse("/admin/cleaners", status_code=303)
    try:
        await cleaner_repo.add(pool, name, email, phone, username, hash_password(password))
        request.session["flash"] = f"Cleaner '{name}' created. They can now log in at /cleaners."
        request.session["flash_type"] = "success"
    except Exception as e:
        msg = str(e)
        if "unique" in msg.lower() or "duplicate" in msg.lower():
            request.session["flash"] = "Username or email already exists."
        else:
            request.session["flash"] = "Failed to create cleaner. Please try again."
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin/cleaners", status_code=303)


async def post_admin_toggle_cleaner(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    cleaner_id = UUID(request.path_params["id"])
    form = await request.form()
    is_active = form.get("is_active", "true").lower() == "true"
    try:
        cleaner = await cleaner_repo.toggle_active(pool, cleaner_id, is_active)
        if cleaner:
            state = "activated" if is_active else "deactivated"
            request.session["flash"] = f"'{cleaner.name}' {state}."
            request.session["flash_type"] = "success"
        else:
            request.session["flash"] = "Cleaner not found."
            request.session["flash_type"] = "error"
    except Exception:
        request.session["flash"] = "Failed to update status."
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin/cleaners", status_code=303)


async def post_admin_delete_cleaner(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    pool = get_pool()
    cleaner_id = UUID(request.path_params["id"])
    try:
        cleaner = await cleaner_repo.get_by_id(pool, cleaner_id)
        name = cleaner.name if cleaner else "Cleaner"
        deleted = await cleaner_repo.delete(pool, cleaner_id)
        if deleted:
            request.session["flash"] = f"'{name}' deleted."
            request.session["flash_type"] = "success"
        else:
            request.session["flash"] = "Cleaner not found."
            request.session["flash_type"] = "error"
    except Exception:
        request.session["flash"] = "Failed to delete cleaner."
        request.session["flash_type"] = "error"
    return RedirectResponse("/admin/cleaners", status_code=303)
