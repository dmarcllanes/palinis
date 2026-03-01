"""
Shared constants for all admin pages.
Import from here — never from another route file.
"""
from services.status_transition_service import ALLOWED_TRANSITIONS
from domain.enums import BookingStatus

# ── Human-readable labels ────────────────────────────────────────────────────
# Admin-facing labels (internal language)
STATUS_LABELS: dict[str, str] = {
    BookingStatus.pending_confirmation.value: "New Booking",
    BookingStatus.confirmed.value:          "Confirmed",
    BookingStatus.assigned.value:           "Cleaner Assigned",
    BookingStatus.in_progress.value:        "In Progress",
    BookingStatus.completed.value:          "Completed",
    BookingStatus.cancelled.value:          "Cancelled",
    BookingStatus.flagged_for_review.value: "Flagged",
}

# Customer-facing labels
CUSTOMER_STATUS_LABELS: dict[str, str] = {
    BookingStatus.pending_confirmation.value: "Awaiting Confirmation",
    BookingStatus.confirmed.value:          "Confirmed",
    BookingStatus.assigned.value:           "Cleaner Assigned",
    BookingStatus.in_progress.value:        "In Progress",
    BookingStatus.completed.value:          "Completed",
    BookingStatus.cancelled.value:          "Cancelled",
    BookingStatus.flagged_for_review.value: "Under Review",
}

# Derive allowed next-states from the canonical service — single source of truth
ALLOWED_NEXT: dict[str, list[str]] = {
    status.value: [s.value for s in targets]
    for status, targets in ALLOWED_TRANSITIONS.items()
}


# ── Shared admin CSS ─────────────────────────────────────────────────────────
ADMIN_CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f1f5f9; }

/* ── Topbar ── */
.admin-topbar { background: #fff; border-bottom: 1px solid #e8edf3; box-shadow: 0 1px 12px rgba(15,63,94,0.07); padding: 0 2rem; height: 60px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; }
.admin-topbar::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #0f3f5e 0%, #1e9a68 100%); }
.admin-topbar { position: sticky; }
.admin-brand { font-weight: 800; font-size: 1rem; color: #0f3f5e; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.5rem; }
.admin-brand-dot { width: 7px; height: 7px; background: #1e9a68; border-radius: 50%; flex-shrink: 0; }
.admin-brand-sub { color: #94a3b8; font-weight: 600; font-size: 0.75rem; margin-left: 0.25rem; }
.topbar-right { display: flex; align-items: center; gap: 0.4rem; }
.topbar-nav-link { padding: 0.38rem 0.85rem; border-radius: 8px; font-size: 0.83rem; font-weight: 600; color: #64748b; text-decoration: none; transition: all 0.2s; white-space: nowrap; }
.topbar-nav-link:hover { background: #f0f7fb; color: #0f3f5e; }
.topbar-nav-link.active { background: #f0f7fb; color: #0f3f5e; }
.topbar-divider { width: 1px; height: 20px; background: #e2e8f0; margin: 0 0.35rem; flex-shrink: 0; }
.topbar-site-link { font-size: 0.82rem; color: #94a3b8; text-decoration: none; font-weight: 500; transition: color 0.2s; white-space: nowrap; padding: 0.38rem 0.6rem; }
.topbar-site-link:hover { color: #0f3f5e; }
.logout-btn { background: #fee2e2; color: #dc2626 !important; padding: 0.35rem 0.9rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 700; border: none; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.logout-btn:hover { background: #fecaca !important; }

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
.badge-pending_confirmation { background: #fef9c3; color: #854d0e; }
.badge-confirmed          { background: #dbeafe; color: #1e40af; }
.badge-assigned           { background: #ede9fe; color: #6d28d9; }
.badge-in_progress        { background: #d1fae5; color: #065f46; }
.badge-completed          { background: #dcfce7; color: #166534; }
.badge-cancelled          { background: #fee2e2; color: #991b1b; }
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
    .admin-topbar { padding: 0 1rem; height: 54px; }
    .admin-brand-sub { display: none; }
    .topbar-divider { display: none; }
    .topbar-site-link { display: none; }
    .topbar-nav-link { padding: 0.32rem 0.6rem; font-size: 0.78rem; }
    .logout-btn { padding: 0.3rem 0.65rem; font-size: 0.78rem; }
    .admin-body { padding: 1rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
"""
