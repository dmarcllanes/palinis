from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse
from admin.cleaner_auth import verify_password
from repositories.db import get_pool
from repositories import cleaner_repo, booking_repo

PORTAL_CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0fdf4; }

/* ── Topbar ── */
.cl-topbar {
    background: #fff;
    border-bottom: 1px solid #e8edf3;
    box-shadow: 0 1px 12px rgba(15,63,94,0.07);
    padding: 0 2rem;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}
.cl-topbar::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #0f3f5e 0%, #1e9a68 100%); }
.cl-brand { font-weight: 800; font-size: 1rem; color: #0f3f5e; display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.01em; }
.cl-brand-dot { width: 7px; height: 7px; background: #1e9a68; border-radius: 50%; flex-shrink: 0; }
.cl-brand-sub { color: #94a3b8; font-weight: 600; font-size: 0.75rem; margin-left: 0.2rem; }
.cl-nav { display: flex; align-items: center; gap: 0.5rem; }
.cl-logout-btn { background: #fee2e2; color: #dc2626; padding: 0.35rem 0.9rem; border-radius: 9999px; font-weight: 700; border: none; cursor: pointer; font-size: 0.82rem; transition: background 0.2s; }
.cl-logout-btn:hover { background: #fecaca; }

/* ── Login page ── */
.login-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0fdf4; }
.login-card { background: #fff; border-radius: 16px; padding: 2.5rem; width: 100%; max-width: 380px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); border: 1.5px solid #bbf7d0; }
.login-logo { font-size: 1rem; font-weight: 800; color: #14532d; margin-bottom: 0.2rem; }
.login-logo span { color: #16a34a; }
.login-card h2 { font-size: 1.2rem; color: #111827; margin: 0 0 1.5rem; font-weight: 700; }
.login-field { margin-bottom: 1rem; }
.login-field label { display: block; font-size: 0.82rem; font-weight: 600; color: #374151; margin-bottom: 0.3rem; }
.login-field input { width: 100%; padding: 0.8rem 1rem; border: 1.5px solid #d1fae5; border-radius: 10px; font-size: 0.95rem; color: #111827; }
.login-field input:focus { outline: none; border-color: #16a34a; }
.login-btn { width: 100%; background: #16a34a; color: #fff; border: none; padding: 0.85rem; border-radius: 9999px; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 0.5rem; transition: background 0.2s; }
.login-btn:hover { background: #15803d; }
.login-error { background: #fee2e2; color: #991b1b; padding: 0.7rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; }
.login-hint { text-align: center; font-size: 0.8rem; color: #9ca3af; margin-top: 1.25rem; }

/* ── Dashboard ── */
.cl-body { max-width: 1000px; margin: 0 auto; padding: 2.5rem 2rem 4rem; }

.cl-welcome { margin-bottom: 2rem; }
.cl-welcome h1 { font-size: 1.5rem; font-weight: 800; color: #14532d; margin: 0 0 0.2rem; }
.cl-welcome p { font-size: 0.9rem; color: #6b7280; margin: 0; }

/* Profile card */
.cl-profile { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1.5px solid #bbf7d0; border-radius: 16px; padding: 1.75rem; margin-bottom: 2rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; box-shadow: 0 2px 12px rgba(22,163,74,0.07); }
.cl-avatar-lg { width: 68px; height: 68px; border-radius: 50%; background: #16a34a; color: #fff; font-size: 1.75rem; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 8px rgba(22,163,74,0.25); }
.cl-profile-info { flex: 1; }
.cl-profile-info h3 { font-size: 1.15rem; font-weight: 800; color: #14532d; margin: 0 0 0.5rem; }
.cl-profile-meta { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; margin-bottom: 0.75rem; }
.cl-meta-item { display: flex; align-items: center; gap: 0.35rem; font-size: 0.83rem; color: #4b5563; }
.cl-meta-icon { font-size: 0.85rem; }
.cl-status-chip { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
.cl-status-chip.active  { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.cl-status-chip.inactive { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

/* Jobs section */
.cl-section-title { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #6b7280; margin: 0 0 1rem; }

.cl-job-card { background: #fff; border: 1.5px solid #e5e7eb; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 0.85rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; transition: border-color 0.2s; }
.cl-job-card:hover { border-color: #86efac; }
.cl-job-info h4 { font-size: 0.92rem; font-weight: 700; color: #111827; margin: 0 0 0.3rem; }
.cl-job-info p { font-size: 0.82rem; color: #6b7280; margin: 0; }
.cl-job-meta { text-align: right; }
.cl-job-meta .price { font-size: 1.1rem; font-weight: 800; color: #15803d; }
.cl-job-meta .date { font-size: 0.8rem; color: #9ca3af; margin-top: 0.2rem; }
.job-badge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
.badge-confirmed    { background: #dbeafe; color: #1e40af; }
.badge-assigned     { background: #ede9fe; color: #6d28d9; }
.badge-in_progress  { background: #d1fae5; color: #065f46; }
.badge-completed    { background: #dcfce7; color: #166534; }

/* ── Tabs ── */
.cl-tabs { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.cl-tab { padding: 0.45rem 1.1rem; border-radius: 20px; border: 1.5px solid #d1fae5; background: #fff; font-size: 0.82rem; font-weight: 600; color: #6b7280; cursor: pointer; transition: all 0.2s; }
.cl-tab:hover { border-color: #16a34a; color: #15803d; }
.cl-tab.active { background: #16a34a; border-color: #16a34a; color: #fff; }

.cl-empty-jobs { text-align: center; padding: 3rem; background: #fff; border-radius: 12px; border: 1.5px dashed #d1fae5; color: #9ca3af; font-size: 0.92rem; }

/* ── Pagination ── */
.cl-pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.25rem; }
.cl-page-btn { background: #fff; border: 1.5px solid #d1fae5; color: #15803d; padding: 0.4rem 1rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.cl-page-btn:hover:not(:disabled) { background: #dcfce7; border-color: #16a34a; }
.cl-page-btn:disabled { opacity: 0.35; cursor: default; }
.cl-page-info { font-size: 0.82rem; color: #6b7280; font-weight: 500; min-width: 80px; text-align: center; }

@media (max-width: 640px) {
    /* Layout */
    .cl-body { padding: 1.25rem 1rem 5rem; }
    .cl-topbar { padding: 0 1rem; height: 54px; }
    .cl-brand { font-size: 0.9rem; }
    .cl-brand-sub { display: none; }

    /* Welcome */
    .cl-welcome { margin-bottom: 1.25rem; }
    .cl-welcome h1 { font-size: 1.2rem; }

    /* Profile card */
    .cl-profile { flex-direction: column; align-items: flex-start; gap: 1rem; padding: 1.25rem; }
    .cl-avatar-lg { width: 56px; height: 56px; font-size: 1.4rem; }
    .cl-profile-info h3 { font-size: 1.05rem; }
    .cl-profile-meta { flex-direction: column; gap: 0.35rem; }
    .cl-meta-item { font-size: 0.8rem; }

    /* Tabs */
    .cl-tabs { gap: 0.4rem; }
    .cl-tab { padding: 0.4rem 0.85rem; font-size: 0.78rem; flex: 1; text-align: center; }

    /* Job cards */
    .cl-job-card { flex-direction: column; align-items: flex-start; gap: 0.75rem; padding: 1rem; }
    .cl-job-meta { text-align: left; width: 100%; display: flex; justify-content: space-between; align-items: center; }
    .cl-job-meta .date { margin-top: 0; }
    .cl-job-info h4 { font-size: 0.88rem; }
    .cl-job-info p { font-size: 0.78rem; }

    /* Pagination */
    .cl-pagination { gap: 0.75rem; }
    .cl-page-btn { padding: 0.4rem 0.85rem; font-size: 0.78rem; }

    /* Login card */
    .login-card { padding: 1.75rem 1.25rem; }
}
"""


def _require_cleaner(request: Request):
    if not request.session.get("cleaner_id"):
        return RedirectResponse("/cleaners", status_code=303)
    return None


def cleaner_login_page(error: str = ""):
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Cleaner Login – Filo Cleaning Services"),
            Style(PORTAL_CSS),
        ),
        Body(
            Div(
                Div(
                    Img(src='/images/logo.png', alt='Filo Logo', style='height: 80px; margin: 0 auto 1rem; display: block;'),
                    P("Filo Cleaning Services", cls="login-logo", style="margin-bottom: 0.25rem; text-align: center;"),
                    H2("Cleaner Sign In", style="margin-top: 0; text-align: center;"),
                    Div(error, cls="login-error") if error else None,
                    Form(
                        Div(
                            Label("Username"),
                            Input(type="text", name="username", placeholder="your.username",
                                  autofocus=True, autocomplete="username"),
                            cls="login-field",
                        ),
                        Div(
                            Label("Password"),
                            Input(type="password", name="password", placeholder="••••••••",
                                  autocomplete="current-password"),
                            cls="login-field",
                        ),
                        Button("Sign In", type="submit", cls="login-btn"),
                        method="POST",
                        action="/cleaners/login",
                    ),
                    P("Your credentials are provided by your manager.", cls="login-hint"),
                    cls="login-card",
                ),
                cls="login-wrap",
            ),
        ),
        lang="en",
    )


def cleaner_dashboard_page(cleaner, jobs):
    svc_label = lambda s: s.replace("_", " ").title()
    UPCOMING = {"assigned", "in_progress"}

    job_cards = []
    for j in jobs:
        badge_cls = f"job-badge badge-{j.status.value}"
        status_text = j.status.value.replace("_", " ").title()
        category = "completed" if j.status.value == "completed" else "upcoming"
        job_cards.append(
            Div(
                Div(
                    H4(svc_label(j.service_type.value)),
                    P(f"{j.address}, {j.postcode} · {j.bedrooms}bd / {j.bathrooms}ba · ",
                      Span(status_text, cls=badge_cls)),
                    cls="cl-job-info",
                ),
                Div(
                    Div(f"${j.total_price}", cls="price"),
                    Div(str(j.service_date), cls="date"),
                    cls="cl-job-meta",
                ),
                cls="cl-job-card",
                data_category=category,
            )
        )

    upcoming_count  = sum(1 for j in jobs if j.status.value in UPCOMING)
    completed_count = sum(1 for j in jobs if j.status.value == "completed")

    tabs = Div(
        Button(f"All ({len(jobs)})",             cls="cl-tab active",    data_tab="all"),
        Button(f"Upcoming ({upcoming_count})",   cls="cl-tab",           data_tab="upcoming"),
        Button(f"Completed ({completed_count})", cls="cl-tab",           data_tab="completed"),
        cls="cl-tabs",
        id="cl-tabs",
    )

    jobs_container = Div(*job_cards, id="cl-jobs") if job_cards else Div(
        "No jobs assigned yet.", cls="cl-empty-jobs"
    )

    pagination = Div(
        Button("← Prev", id="cl-prev", cls="cl-page-btn"),
        Span("", id="cl-page-info", cls="cl-page-info"),
        Button("Next →", id="cl-next", cls="cl-page-btn"),
        id="cl-pagination",
        cls="cl-pagination",
    )

    tab_script = Script("""
        var PAGE_SIZE = 5;
        var currentTab = 'all';
        var currentPage = 1;

        function getVisible() {
            return Array.from(document.querySelectorAll('#cl-jobs .cl-job-card')).filter(function(card) {
                return currentTab === 'all' || card.dataset.category === currentTab;
            });
        }

        function render() {
            var cards = getVisible();
            var total = cards.length;
            var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
            if (currentPage > pages) currentPage = 1;
            var start = (currentPage - 1) * PAGE_SIZE;
            Array.from(document.querySelectorAll('#cl-jobs .cl-job-card')).forEach(function(card) {
                card.style.display = 'none';
            });
            cards.slice(start, start + PAGE_SIZE).forEach(function(card) {
                card.style.display = '';
            });
            document.getElementById('cl-page-info').textContent = total === 0 ? 'No jobs' : 'Page ' + currentPage + ' of ' + pages;
            document.getElementById('cl-prev').disabled = currentPage <= 1;
            document.getElementById('cl-next').disabled = currentPage >= pages;
            document.getElementById('cl-pagination').style.display = total === 0 ? 'none' : '';
        }

        document.getElementById('cl-tabs').addEventListener('click', function(e) {
            var btn = e.target.closest('.cl-tab');
            if (!btn) return;
            document.querySelectorAll('.cl-tab').forEach(function(t) { t.classList.remove('active'); });
            btn.classList.add('active');
            currentTab = btn.dataset.tab;
            currentPage = 1;
            render();
        });

        document.getElementById('cl-prev').addEventListener('click', function() {
            if (currentPage > 1) { currentPage--; render(); }
        });
        document.getElementById('cl-next').addEventListener('click', function() {
            var pages = Math.max(1, Math.ceil(getVisible().length / PAGE_SIZE));
            if (currentPage < pages) { currentPage++; render(); }
        });

        render();
    """)

    avatar = (cleaner.name[0] if cleaner.name else "?").upper()

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Meta(http_equiv="Cache-Control", content="no-store, no-cache, must-revalidate"),
            Title(f"{cleaner.name} – Cleaner Portal"),
            Style(PORTAL_CSS),
        ),
        Body(
            Div(
                A(
                    Img(src='/images/logo.png', alt='Logo', style='height: 24px;'),
                    "Filo Cleaning Services",
                    Span("· Portal", cls="cl-brand-sub"),
                    cls="cl-brand",
                    href="/cleaners/dashboard",
                    style="display: flex; align-items: center; gap: 0.5rem; text-decoration: none;"
                ),
                Div(
                    Form(Button("Sign Out", cls="cl-logout-btn"),
                         method="POST", action="/cleaners/logout", hx_boost="false"),
                    cls="cl-nav",
                ),
                cls="cl-topbar",
            ),
            Div(
                Div(
                    H1(f"Hi, {cleaner.name.split()[0]}!"),
                    P("Here's your upcoming work schedule."),
                    cls="cl-welcome",
                ),

                # Profile
                Div(
                    Div(avatar, cls="cl-avatar-lg"),
                    Div(
                        H3(cleaner.name),
                        Div(
                            Div(Span("✉", cls="cl-meta-icon"), cleaner.email, cls="cl-meta-item"),
                            Div(Span("📞", cls="cl-meta-icon"), cleaner.phone, cls="cl-meta-item") if cleaner.phone else None,
                            Div(Span("👤", cls="cl-meta-icon"), f"@{cleaner.username}", cls="cl-meta-item") if cleaner.username else None,
                            cls="cl-profile-meta",
                        ),
                        Span(
                            "● Active" if cleaner.is_active else "● Inactive",
                            cls=f"cl-status-chip {'active' if cleaner.is_active else 'inactive'}",
                        ),
                        cls="cl-profile-info",
                    ),
                    cls="cl-profile",
                ),

                P("Jobs", cls="cl-section-title"),
                tabs,
                jobs_container,
                pagination,
                tab_script,

                cls="cl-body",
            ),
        ),
        lang="en",
    )


# ── Route handlers ──

async def get_cleaner_login(request: Request):
    if request.session.get("cleaner_id"):
        return RedirectResponse("/cleaners/dashboard", status_code=303)
    return cleaner_login_page()


async def post_cleaner_login(request: Request):
    pool = get_pool()
    form = await request.form()
    username = (form.get("username") or "").strip()
    password = (form.get("password") or "")
    if not username or not password:
        return cleaner_login_page(error="Please enter your username and password.")
    cleaner = await cleaner_repo.get_by_username(pool, username)
    if not cleaner or not cleaner.password_hash or not verify_password(password, cleaner.password_hash):
        return cleaner_login_page(error="Incorrect username or password.")
    if not cleaner.is_active:
        return cleaner_login_page(error="Your account has been deactivated. Contact your manager.")
    request.session["cleaner_id"] = str(cleaner.id)
    request.session["cleaner_name"] = cleaner.name
    return RedirectResponse("/cleaners/dashboard", status_code=303)


async def get_cleaner_dashboard(request: Request):
    redirect = _require_cleaner(request)
    if redirect:
        return redirect
    pool = get_pool()
    from uuid import UUID
    cleaner_id = UUID(request.session["cleaner_id"])
    cleaner = await cleaner_repo.get_by_id(pool, cleaner_id)
    if not cleaner:
        request.session.clear()
        return RedirectResponse("/cleaners", status_code=303)
    # Show only bookings assigned to this cleaner
    jobs = await booking_repo.get_by_cleaner_id(pool, cleaner_id)
    return cleaner_dashboard_page(cleaner, jobs)


async def post_cleaner_logout(request: Request):
    request.session.pop("cleaner_id", None)
    request.session.pop("cleaner_name", None)
    return RedirectResponse("/cleaners", status_code=303)
