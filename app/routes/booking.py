from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from pydantic import ValidationError
from domain.booking import CreateBookingRequest
from services import booking_service, availability_service
from repositories.db import get_pool
from components.admin_ui import CUSTOMER_STATUS_LABELS
from datetime import date as date_type

BOOKING_NAV_CSS = """
.book-nav {
    background: #fff;
    border-bottom: 1px solid #e8edf3;
    box-shadow: 0 1px 16px rgba(15,63,94,0.07);
    padding: 0 2rem;
    height: 62px;
    display: flex;
    align-items: center;
    position: relative;
}
.book-nav::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0f3f5e 0%, #1e9a68 100%);
}
.book-nav-inner {
    max-width: 900px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.book-nav-logo {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f3f5e;
    letter-spacing: -0.01em;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.book-nav-dot {
    width: 8px;
    height: 8px;
    background: #1e9a68;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.book-nav-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.book-nav-link {
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748b;
    text-decoration: none;
    transition: color 0.2s;
}
.book-nav-link:hover { color: #0f3f5e; }
.book-nav-pill {
    font-size: 0.82rem;
    font-weight: 700;
    color: #0f3f5e;
    border: 1.5px solid #0f3f5e;
    padding: 0.38rem 1rem;
    border-radius: 9999px;
    text-decoration: none;
    transition: all 0.2s;
    white-space: nowrap;
}
.book-nav-pill:hover { background: #0f3f5e; color: #fff; }
@media (max-width: 600px) {
    .book-nav { padding: 0 1rem; height: 54px; }
    .book-nav-logo { font-size: 0.95rem; }
    .book-nav-link { display: none; }
    .book-nav-pill { font-size: 0.78rem; padding: 0.32rem 0.8rem; }
}
"""


def booking_nav(right_links=None):
    """Modern flat navbar for booking-flow pages."""
    if right_links is None:
        right_links = [
            A("Track Booking", href="/booking/lookup", cls="book-nav-link"),
            A("Home", href="/", cls="book-nav-pill"),
        ]
    return Nav(
        Div(
            A(
                Img(src='/images/logo.png', alt='Logo', style='height: 24px; margin-right: 8px; vertical-align: middle;'),
                "Filo Cleaning Services",
                href="/",
                cls="book-nav-logo",
                style="display: flex; align-items: center; text-decoration: none;"
            ),
            Div(*right_links, cls="book-nav-right"),
            cls="book-nav-inner",
        ),
        cls="book-nav",
    )


WIZARD_CSS = """
/* ── Base ── */
.booking-page { min-height: 100vh; background: #f8f9fb; padding: 0 0 5rem; }
.wizard-container { max-width: 660px; margin: 2rem auto 0; padding: 0 1.5rem; }

/* ── Progress ── */
.wizard-progress { display: flex; align-items: center; justify-content: center; margin-bottom: 2.5rem; }
.progress-step { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; }
.step-num { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; background: var(--bg-light, #e2e8f0); color: var(--text-light, #94a3b8); transition: all 0.3s; }
.progress-step.active .step-num { background: var(--primary, #0f3f5e); color: #fff; }
.progress-step.done .step-num { background: var(--accent, #1e9a68); color: #fff; }
.step-label { font-size: 0.68rem; color: var(--text-light, #94a3b8); font-weight: 500; white-space: nowrap; }
.progress-step.active .step-label, .progress-step.done .step-label { color: var(--primary, #0f3f5e); }
.progress-line { flex: 1; height: 2px; background: var(--border, #e2e8f0); max-width: 50px; margin-bottom: 1.3rem; transition: background 0.3s; }
.progress-line.done { background: var(--accent, #1e9a68); }

/* ── Card ── */
.wizard-card { background: #fff; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.06); }
.wizard-step { display: none; }
.wizard-step.active { display: block; }
.step-title { font-size: 1.4rem; font-weight: 700; color: #0f2d40; margin: 0 0 0.4rem; }
.step-subtitle { color: #64748b; margin: 0 0 1.75rem; font-size: 0.95rem; }

/* ── Service cards ── */
.service-options { display: flex; flex-direction: column; gap: 0.85rem; }
.service-option { border: 2px solid var(--border, #e2e8f0); border-radius: 12px; padding: 1.1rem 1.25rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 1rem; user-select: none; }
.service-option:hover { border-color: var(--primary, #0f3f5e); background: var(--bg-light, #f0f7fb); }
.service-option.selected { border-color: var(--primary, #0f3f5e); background: var(--bg-light, #f0f7fb); }
.svc-icon { font-size: 1.8rem; flex-shrink: 0; }
.svc-info h3 { font-size: 0.95rem; font-weight: 700; color: var(--text-dark, #0f172a); margin: 0 0 0.2rem; }
.svc-info p { font-size: 0.82rem; color: var(--text-light, #64748b); margin: 0; }
.svc-price { margin-left: auto; font-weight: 700; color: var(--primary, #0f3f5e); font-size: 0.95rem; white-space: nowrap; }

/* ── Number selectors ── */
.selector-group { margin-bottom: 1.5rem; }
.selector-label { font-weight: 600; color: #0f2d40; margin-bottom: 0.75rem; display: block; font-size: 0.95rem; }
.num-selector { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.num-btn { width: 52px; height: 52px; border: 2px solid var(--border, #e2e8f0); border-radius: 10px; background: #fff; font-size: 1rem; font-weight: 600; color: var(--text-light, #64748b); cursor: pointer; transition: all 0.2s; }
.num-btn:hover { border-color: var(--primary, #0f3f5e); color: var(--primary, #0f3f5e); }
.num-btn.selected { border-color: var(--primary, #0f3f5e); background: var(--primary, #0f3f5e); color: #fff; }

/* ── Price preview ── */
.price-preview { background: var(--bg-light, #f0f7fb); border-radius: 12px; padding: 1.1rem 1.25rem; margin-top: 1.75rem; display: flex; align-items: center; justify-content: space-between; }
.preview-label { color: var(--text-light, #64748b); font-size: 0.88rem; }
.preview-amount { font-size: 1.9rem; font-weight: 800; color: var(--primary, #0f3f5e); }

/* ── Date picker ── */
.date-picker-wrap { margin-top: 0.5rem; }
.date-picker-wrap input[type=date] { width: 100%; padding: 0.85rem 1rem; border: 2px solid var(--border, #e2e8f0); border-radius: 12px; font-size: 1.05rem; color: var(--text-dark, #0f172a); background: #fff; box-sizing: border-box; }
.date-picker-wrap input[type=date]:focus { outline: none; border-color: var(--primary, #0f3f5e); }

/* ── Form fields ── */
.form-group { margin-bottom: 1.1rem; }
.form-group label { display: block; font-weight: 600; color: var(--text-dark, #0f172a); margin-bottom: 0.35rem; font-size: 0.88rem; }
.form-group input { width: 100%; padding: 0.75rem 1rem; border: 2px solid var(--border, #e2e8f0); border-radius: 10px; font-size: 0.95rem; color: var(--text-dark, #0f172a); transition: border-color 0.2s; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: var(--primary, #0f3f5e); }
.field-error { color: #ef4444; font-size: 0.78rem; margin-top: 0.2rem; display: block; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

/* ── Review ── */
.review-section { margin-bottom: 1.25rem; }
.review-section-title { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.07em; color: #94a3b8; font-weight: 600; margin-bottom: 0.6rem; }
.review-row { display: flex; justify-content: space-between; padding: 0.55rem 0; border-bottom: 1px solid #f1f5f9; }
.review-row:last-child { border-bottom: none; }
.r-label { color: #64748b; font-size: 0.88rem; }
.r-value { font-weight: 600; color: #0f2d40; font-size: 0.88rem; }
.total-row { background: var(--bg-light, #f0f7fb); border-radius: 12px; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; margin-top: 1.25rem; }
.total-label { font-weight: 700; color: var(--text-dark, #0f172a); }
.total-amount { font-size: 1.6rem; font-weight: 800; color: var(--primary, #0f3f5e); }

/* ── Nav buttons ── */
.wizard-nav { display: flex; gap: 0.75rem; margin-top: 2rem; }
.btn-back { background: none; border: 2px solid var(--border, #e2e8f0); color: var(--text-light, #64748b); padding: 0.75rem 1.25rem; border-radius: 9999px; font-weight: 600; cursor: pointer; font-size: 0.95rem; }
.btn-back:hover { border-color: var(--text-light, #94a3b8); color: var(--text-light, #475569); }
.btn-next { background: var(--primary, #0f3f5e); color: #fff; border: none; padding: 0.75rem 2rem; border-radius: 9999px; font-weight: 700; cursor: pointer; font-size: 0.95rem; flex: 1; }
.btn-next:hover { background: var(--primary-light, #1e628f); }
.btn-submit { background: var(--accent, #1e9a68); color: #fff; border: none; padding: 0.75rem 2rem; border-radius: 9999px; font-weight: 700; cursor: pointer; font-size: 0.95rem; flex: 1; }
.btn-submit:hover { background: #15803d; }

/* ── Error banner ── */
.error-banner { background: #fef2f2; border: 1.5px solid #fecaca; color: #dc2626; padding: 0.85rem 1rem; border-radius: 10px; margin-bottom: 1.25rem; font-size: 0.88rem; }

.back-home-link { font-size: 0.88rem; color: #64748b; text-decoration: none; font-weight: 500; margin-left: auto; }
.back-home-link:hover { color: #1a4d6d; }

/* ── Time slots ── */
.time-slots-wrap { margin-top: 1.25rem; }
.time-slots-label { font-weight: 600; color: #0f2d40; margin-bottom: 0.75rem; display: block; font-size: 0.95rem; }
.time-slots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 0.6rem; }
.time-slot-btn { border: 2px solid var(--border, #e2e8f0); border-radius: 10px; padding: 0.65rem 0.5rem; background: #fff; font-size: 0.9rem; font-weight: 600; color: var(--text-dark, #0f172a); cursor: pointer; text-align: center; transition: all 0.2s; }
.time-slot-btn:hover:not(.slot-full) { border-color: var(--primary, #0f3f5e); color: var(--primary, #0f3f5e); }
.time-slot-btn.selected { border-color: var(--primary, #0f3f5e); background: var(--primary, #0f3f5e); color: #fff; }
.time-slot-btn.slot-full { border-color: #e2e8f0; background: #f8f9fb; color: #94a3b8; cursor: not-allowed; text-decoration: line-through; }
.slots-loading { color: #64748b; font-size: 0.9rem; padding: 0.5rem 0; }
.slots-empty { color: #94a3b8; font-size: 0.88rem; padding: 0.5rem 0; }

/* ── Mobile ── */
@media (max-width: 600px) {
    .booking-page { padding: 0 0 5rem; }
    .wizard-container { margin: 1rem auto 0; padding: 0 1rem; }
    .wizard-card { padding: 1.25rem 1rem; border-radius: 12px; }

    /* Progress: hide labels, shrink circles */
    .step-label { display: none; }
    .step-num { width: 30px; height: 30px; font-size: 0.78rem; }
    .progress-line { max-width: 28px; margin-bottom: 0; }
    .wizard-progress { margin-bottom: 1.5rem; gap: 0; }

    /* Titles */
    .step-title { font-size: 1.15rem; }
    .step-subtitle { font-size: 0.85rem; margin-bottom: 1.25rem; }

    /* Service cards */
    .service-option { padding: 0.9rem 1rem; gap: 0.75rem; }
    .svc-icon { font-size: 1.5rem; }
    .svc-info h3 { font-size: 0.88rem; }
    .svc-info p { font-size: 0.78rem; }
    .svc-price { font-size: 0.85rem; }

    /* Number buttons - bigger touch targets */
    .num-btn { width: 56px; height: 56px; font-size: 1.05rem; border-radius: 12px; }

    /* Price preview */
    .preview-amount { font-size: 1.5rem; }

    /* Date input */
    .date-picker-wrap input[type=date] { font-size: 1rem; padding: 0.9rem 1rem; }

    /* Form fields */
    .form-group input { font-size: 1rem; padding: 0.85rem 1rem; }
    .form-row { grid-template-columns: 1fr; }

    /* Wizard nav buttons - full width stacked */
    .wizard-nav { flex-direction: column-reverse; margin-top: 1.5rem; }
    .btn-next, .btn-submit { width: 100%; padding: 1rem; font-size: 1rem; }
    .btn-back { width: 100%; padding: 0.85rem; text-align: center; }

    /* Review */
    .total-amount { font-size: 1.3rem; }

    /* Navbar */
    .back-home-link { font-size: 0.8rem; }
}
"""

WIZARD_JS = """
const BASE_PRICES = {
    regular:      {1: 89,  2: 135, 3: 165, 4: 195, 5: 225},
    deep:         {1: 149, 2: 189, 3: 245, 4: 299, 5: 349},
    end_of_lease: {1: 199, 2: 299, 3: 399, 4: 499, 5: 599},
};
const BATH_MULT = {1: 1.0, 2: 1.15, 3: 1.3, 4: 1.45};

const state = { service_type: '', bedrooms: 2, bathrooms: 1, service_date: '', service_time: '' };
let currentStep = 1;

function calcPrice() {
    if (!state.service_type) return 0;
    const base = BASE_PRICES[state.service_type]?.[state.bedrooms] || 0;
    return Math.round(base * (BATH_MULT[state.bathrooms] || 1) * 100) / 100;
}

function fmt(p) { return '$' + p.toFixed(2); }

function showStep(n) {
    document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
    document.getElementById('step-' + n).classList.add('active');
    document.querySelectorAll('.progress-step').forEach((el, i) => {
        el.classList.remove('active', 'done');
        if (i + 1 === n) el.classList.add('active');
        else if (i + 1 < n) el.classList.add('done');
    });
    document.querySelectorAll('.progress-line').forEach((el, i) => {
        el.classList.toggle('done', i + 1 < n);
    });
    currentStep = n;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectService(type) {
    state.service_type = type;
    document.getElementById('input-service-type').value = type;
    document.querySelectorAll('.service-option').forEach(el => {
        el.classList.toggle('selected', el.dataset.type === type);
    });
    setTimeout(() => showStep(2), 250);
}

function selectNum(type, val) {
    state[type] = val;
    document.getElementById('input-' + type).value = val;
    document.querySelectorAll(`.num-btn[data-type="${type}"]`).forEach(btn => {
        btn.classList.toggle('selected', parseInt(btn.dataset.val) === val);
    });
    const el = document.getElementById('price-preview-amount');
    if (el) el.textContent = fmt(calcPrice());
}

function selectTimeSlot(value, label, btn) {
    if (btn.classList.contains('slot-full')) return;
    state.service_time = value;
    document.getElementById('input-service-time').value = value;
    document.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
}

async function loadTimeSlots(dateStr) {
    const wrap = document.getElementById('time-slots-container');
    if (!wrap) return;
    wrap.innerHTML = '<p class="slots-loading">Checking availability…</p>';
    state.service_time = '';
    document.getElementById('input-service-time').value = '';

    try {
        const resp = await fetch('/book/slots?date=' + encodeURIComponent(dateStr));
        const data = await resp.json();
        if (!data.slots || data.slots.length === 0) {
            wrap.innerHTML = '<p class="slots-empty">No availability on this date. Please choose another day.</p>';
            return;
        }
        const allSlots = [
            {value: '08:00:00', label: '8:00 AM'},
            {value: '10:00:00', label: '10:00 AM'},
            {value: '12:00:00', label: '12:00 PM'},
            {value: '14:00:00', label: '2:00 PM'},
            {value: '16:00:00', label: '4:00 PM'},
        ];
        const available = new Set(data.slots);
        const grid = document.createElement('div');
        grid.className = 'time-slots-grid';
        allSlots.forEach(s => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'time-slot-btn' + (available.has(s.value) ? '' : ' slot-full');
            btn.textContent = s.label + (available.has(s.value) ? '' : ' ✕');
            if (available.has(s.value)) {
                btn.onclick = () => selectTimeSlot(s.value, s.label, btn);
            }
            grid.appendChild(btn);
        });
        wrap.innerHTML = '';
        wrap.appendChild(grid);
    } catch(e) {
        wrap.innerHTML = '<p class="slots-empty">Could not load availability. Please try again.</p>';
    }
}

function populateReview() {
    const labels = { regular: 'Regular Cleaning', deep: 'Deep Cleaning', end_of_lease: 'End of Lease' };
    const timeLabels = {
        '08:00:00': '8:00 AM', '10:00:00': '10:00 AM', '12:00:00': '12:00 PM',
        '14:00:00': '2:00 PM', '16:00:00': '4:00 PM'
    };
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    set('review-service',   labels[state.service_type] || '');
    set('review-property',  state.bedrooms + ' bed · ' + state.bathrooms + ' bath');
    const timeLabel = timeLabels[state.service_time] || state.service_time;
    set('review-date',      document.getElementById('input-service-date').value + ' at ' + timeLabel);
    set('review-name',      document.getElementById('f-name').value);
    set('review-email',     document.getElementById('f-email').value);
    set('review-phone',     document.getElementById('f-phone').value);
    set('review-address',   document.getElementById('f-address').value + ', ' + document.getElementById('f-postcode').value);
    set('review-total',     fmt(calcPrice()));
}

function showFieldError(id, msg) {
    const input = document.getElementById(id);
    input.style.borderColor = '#ef4444';
    let err = input.parentElement.querySelector('.inline-error');
    if (!err) {
        err = document.createElement('span');
        err.className = 'field-error inline-error';
        input.parentElement.appendChild(err);
    }
    err.textContent = msg;
}

function clearFieldErrors() {
    document.querySelectorAll('.inline-error').forEach(el => el.remove());
    document.querySelectorAll('#step-4 input').forEach(el => el.style.borderColor = '');
}

function goNext() {
    if (currentStep === 1) {
        if (!state.service_type) { alert('Please select a service type.'); return; }
    }
    if (currentStep === 3) {
        const d = document.getElementById('input-service-date').value;
        if (!d) { alert('Please select a date.'); return; }
        const picked = new Date(d);
        const today = new Date(); today.setHours(0,0,0,0);
        if (picked < today) { alert('Please select a future date.'); return; }
        state.service_date = d;
        if (!state.service_time) { alert('Please select a time slot.'); return; }
    }
    if (currentStep === 4) {
        clearFieldErrors();
        let valid = true;
        const name     = document.getElementById('f-name').value.trim();
        const email    = document.getElementById('f-email').value.trim();
        const phone    = document.getElementById('f-phone').value.trim();
        const address  = document.getElementById('f-address').value.trim();
        const postcode = document.getElementById('f-postcode').value.trim();

        if (!name)    { showFieldError('f-name', 'Name is required.'); valid = false; }
        if (!email)   { showFieldError('f-email', 'Email is required.'); valid = false; }
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            showFieldError('f-email', 'Please enter a valid email address.'); valid = false;
        }
        if (!phone)   { showFieldError('f-phone', 'Phone is required.'); valid = false; }
        if (!address) { showFieldError('f-address', 'Address is required.'); valid = false; }
        if (!postcode) { showFieldError('f-postcode', 'Postcode is required.'); valid = false; }
        else if (!/^\d{4}$/.test(postcode)) {
            showFieldError('f-postcode', 'Postcode must be 4 digits.'); valid = false;
        }

        if (!valid) return;
        populateReview();
    }
    if (currentStep < 5) showStep(currentStep + 1);
}

function goBack() {
    if (currentStep > 1) showStep(currentStep - 1);
}

window.addEventListener('DOMContentLoaded', () => {
    showStep(1);
    selectNum('bedrooms', 2);
    selectNum('bathrooms', 1);

    const dateInput = document.getElementById('input-service-date');
    if (dateInput) {
        dateInput.addEventListener('change', () => {
            const d = dateInput.value;
            if (d) loadTimeSlots(d);
        });
    }
});
"""


def booking_form_page(errors: dict = {}):
    error_banner = None
    if errors:
        msg = next(iter(errors.values()))
        error_banner = Div(f"⚠ {msg}", cls="error-banner")

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Title("Book a Cleaning – Filo Cleaning Services"),
            Link(rel="stylesheet", href="/css/styles.css"),
            Style(BOOKING_NAV_CSS),
            Style(WIZARD_CSS),
        ),
        Body(
            Main(
                booking_nav(),
                Div(
                    # Progress bar
                    Div(
                        Div(Div("1", cls="step-num"), Span("Service", cls="step-label"), cls="progress-step active"),
                        Div(cls="progress-line"),
                        Div(Div("2", cls="step-num"), Span("Property", cls="step-label"), cls="progress-step"),
                        Div(cls="progress-line"),
                        Div(Div("3", cls="step-num"), Span("Date", cls="step-label"), cls="progress-step"),
                        Div(cls="progress-line"),
                        Div(Div("4", cls="step-num"), Span("Details", cls="step-label"), cls="progress-step"),
                        Div(cls="progress-line"),
                        Div(Div("5", cls="step-num"), Span("Review", cls="step-label"), cls="progress-step"),
                        cls="wizard-progress",
                    ),

                    # Form
                    Form(
                        # Hidden inputs populated by JS
                        Input(type="hidden", name="service_type",  id="input-service-type"),
                        Input(type="hidden", name="bedrooms",      id="input-bedrooms", value="2"),
                        Input(type="hidden", name="bathrooms",     id="input-bathrooms", value="1"),
                        Input(type="hidden", name="service_time",  id="input-service-time"),

                        # ── Step 1: Service Type ──
                        Div(
                            Div(
                                error_banner,
                                H2("What type of cleaning?", cls="step-title"),
                                P("Select the service that fits your needs.", cls="step-subtitle"),
                                Div(
                                    Div(
                                        Span("🧹", cls="svc-icon"),
                                        Div(H3("Regular Cleaning"), P("Weekly or fortnightly upkeep"), cls="svc-info"),
                                        Span("From $89", cls="svc-price"),
                                        cls="service-option", data_type="regular",
                                        onclick="selectService('regular')",
                                    ),
                                    Div(
                                        Span("✨", cls="svc-icon"),
                                        Div(H3("Deep Cleaning"), P("Seasonal refresh or detailed reset"), cls="svc-info"),
                                        Span("From $149", cls="svc-price"),
                                        cls="service-option", data_type="deep",
                                        onclick="selectService('deep')",
                                    ),
                                    Div(
                                        Span("🏠", cls="svc-icon"),
                                        Div(H3("End of Lease"), P("Bond-back guarantee for rentals"), cls="svc-info"),
                                        Span("From $199", cls="svc-price"),
                                        cls="service-option", data_type="end_of_lease",
                                        onclick="selectService('end_of_lease')",
                                    ),
                                    cls="service-options",
                                ),
                            ),
                            cls="wizard-card wizard-step", id="step-1",
                        ),

                        # ── Step 2: Property Size ──
                        Div(
                            Div(
                                H2("Your property", cls="step-title"),
                                P("This helps us calculate your price accurately.", cls="step-subtitle"),
                                Div(
                                    Span("Bedrooms", cls="selector-label"),
                                    Div(
                                        *[Button(str(n), type="button", cls="num-btn", data_type="bedrooms",
                                                 data_val=str(n), onclick=f"selectNum('bedrooms',{n})")
                                          for n in range(1, 6)],
                                        cls="num-selector",
                                    ),
                                    cls="selector-group",
                                ),
                                Div(
                                    Span("Bathrooms", cls="selector-label"),
                                    Div(
                                        *[Button(str(n), type="button", cls="num-btn", data_type="bathrooms",
                                                 data_val=str(n), onclick=f"selectNum('bathrooms',{n})")
                                          for n in range(1, 5)],
                                        cls="num-selector",
                                    ),
                                    cls="selector-group",
                                ),
                                Div(
                                    Span("Estimated price", cls="preview-label"),
                                    Span("$0.00", cls="preview-amount", id="price-preview-amount"),
                                    cls="price-preview",
                                ),
                                Div(
                                    Button("← Back", cls="btn-back", type="button", onclick="goBack()"),
                                    Button("Next →", cls="btn-next", type="button", onclick="goNext()"),
                                    cls="wizard-nav",
                                ),
                            ),
                            cls="wizard-card wizard-step", id="step-2",
                        ),

                        # ── Step 3: Date & Time ──
                        Div(
                            Div(
                                H2("Pick a date & time", cls="step-title"),
                                P("Choose your preferred cleaning date and available time slot.", cls="step-subtitle"),
                                Div(
                                    Input(type="date", id="input-service-date", name="service_date"),
                                    cls="date-picker-wrap",
                                ),
                                Div(
                                    Span("Available time slots", cls="time-slots-label"),
                                    Div(
                                        P("Select a date above to see available times.", cls="slots-empty"),
                                        id="time-slots-container",
                                    ),
                                    cls="time-slots-wrap",
                                ),
                                Div(
                                    Button("← Back", cls="btn-back", type="button", onclick="goBack()"),
                                    Button("Next →", cls="btn-next", type="button", onclick="goNext()"),
                                    cls="wizard-nav",
                                ),
                            ),
                            cls="wizard-card wizard-step", id="step-3",
                        ),

                        # ── Step 4: Contact Details ──
                        Div(
                            Div(
                                H2("Your details", cls="step-title"),
                                P("We'll use these to confirm your booking.", cls="step-subtitle"),
                                Div(
                                    Label("Full Name", fr="f-name"),
                                    Input(type="text", id="f-name", name="customer_name", placeholder="Jane Smith"),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Email Address", fr="f-email"),
                                    Input(type="email", id="f-email", name="email", placeholder="jane@example.com"),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Phone Number", fr="f-phone"),
                                    Input(type="tel", id="f-phone", name="phone", placeholder="04xx xxx xxx"),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Street Address", fr="f-address"),
                                    Input(type="text", id="f-address", name="address", placeholder="10 George Street"),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Postcode", fr="f-postcode"),
                                    Input(type="text", id="f-postcode", name="postcode",
                                          placeholder="2000", maxlength="4"),
                                    cls="form-group",
                                ),
                                Div(
                                    Button("← Back", cls="btn-back", type="button", onclick="goBack()"),
                                    Button("Next →", cls="btn-next", type="button", onclick="goNext()"),
                                    cls="wizard-nav",
                                ),
                            ),
                            cls="wizard-card wizard-step", id="step-4",
                        ),

                        # ── Step 5: Review ──
                        Div(
                            Div(
                                H2("Review your booking", cls="step-title"),
                                P("Check everything looks right before confirming.", cls="step-subtitle"),

                                Div(
                                    P("Service", cls="review-section-title"),
                                    Div(Span("Type", cls="r-label"), Span("—", cls="r-value", id="review-service"), cls="review-row"),
                                    Div(Span("Property", cls="r-label"), Span("—", cls="r-value", id="review-property"), cls="review-row"),
                                    Div(Span("Date & Time", cls="r-label"), Span("—", cls="r-value", id="review-date"), cls="review-row"),
                                    cls="review-section",
                                ),
                                Div(
                                    P("Contact", cls="review-section-title"),
                                    Div(Span("Name", cls="r-label"), Span("—", cls="r-value", id="review-name"), cls="review-row"),
                                    Div(Span("Email", cls="r-label"), Span("—", cls="r-value", id="review-email"), cls="review-row"),
                                    Div(Span("Phone", cls="r-label"), Span("—", cls="r-value", id="review-phone"), cls="review-row"),
                                    Div(Span("Address", cls="r-label"), Span("—", cls="r-value", id="review-address"), cls="review-row"),
                                    cls="review-section",
                                ),
                                Div(
                                    Span("Total Price", cls="total-label"),
                                    Span("—", cls="total-amount", id="review-total"),
                                    cls="total-row",
                                ),
                                Div(
                                    Button("← Back", cls="btn-back", type="button", onclick="goBack()"),
                                    Button("✓ Confirm Booking", cls="btn-submit", type="submit"),
                                    cls="wizard-nav",
                                ),
                            ),
                            cls="wizard-card wizard-step", id="step-5",
                        ),

                        method="POST",
                        action="/book",
                        id="booking-wizard",
                    ),
                    cls="wizard-container",
                ),
                cls="booking-page",
            ),
            Div(
                Div(
                    Div(
                        Span('✨ New Customer Offer: ', cls='banner-badge'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        
                        Span('✨ New Customer Offer: ', cls='banner-badge', style='margin-left: 2rem;'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        cls='marquee-inner'
                    ),
                    cls='banner-content marquee'
                ),
                cls='announcement-banner',
                style='position: fixed; bottom: 0; left: 0; width: 100%; z-index: 1000;'
            ),
            Script(WIZARD_JS),
        ),
        lang="en",
    )


def booking_confirmation_page(booking):
    service_label = booking.service_type.value.replace("_", " ").title()
    status_label = booking.status.value.replace("_", " ").title()
    time_label = booking.service_time.strftime("%-I:%M %p") if booking.service_time else "—"
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Title("Booking Confirmed – Filo Cleaning Services"),
            Link(rel="stylesheet", href="/css/styles.css"),
            Style(BOOKING_NAV_CSS),
            Style("""
                .confirmation-page { min-height: 100vh; background: #f8f9fb; padding: 0 0 5rem; }
                .confirmation-card { background: #fff; border-radius: 16px; padding: 2.5rem; box-shadow: 0 2px 20px rgba(0,0,0,0.06); max-width: 560px; margin: 2rem auto 0; text-align: center; }
                .success-icon { width: 64px; height: 64px; background: #dcfce7; border-radius: 50%; font-size: 1.8rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem; }
                .confirmation-card h1 { font-size: 1.6rem; color: #0f2d40; margin: 0 0 0.5rem; }
                .confirmation-card > p { color: #64748b; margin: 0 0 2rem; }
                .booking-details { text-align: left; border: 1.5px solid #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 2rem; }
                .detail-row { display: flex; justify-content: space-between; padding: 0.8rem 1.25rem; border-bottom: 1px solid #f1f5f9; }
                .detail-row:last-child { border-bottom: none; }
                .detail-label { color: #64748b; font-size: 0.88rem; }
                .detail-value { font-weight: 600; color: #0f2d40; font-size: 0.88rem; }
                .booking-id { font-family: monospace; font-size: 0.75rem; color: #64748b; }
                .price-highlight { color: #1a4d6d; font-size: 1rem; }
                .status-badge { background: #fef9c3; color: #854d0e; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.78rem; }
            """),
        ),
        Body(
            Main(
                booking_nav(right_links=[
                    A("Track Booking", href="/booking/lookup", cls="book-nav-link"),
                    A("Book Again", href="/book", cls="book-nav-pill"),
                ]),
                Div(
                    Div(
                        Div("✓", cls="success-icon"),
                        H1("Booking Received!"),
                        P("Thank you! We'll be in touch shortly to confirm your appointment."),
                        Div(
                            Div(Span("Booking ID", cls="detail-label"), Span(str(booking.id), cls="detail-value booking-id"), cls="detail-row"),
                            Div(Span("Name", cls="detail-label"), Span(booking.customer_name, cls="detail-value"), cls="detail-row"),
                            Div(Span("Service", cls="detail-label"), Span(service_label, cls="detail-value"), cls="detail-row"),
                            Div(Span("Date", cls="detail-label"), Span(str(booking.service_date), cls="detail-value"), cls="detail-row"),
                            Div(Span("Time", cls="detail-label"), Span(time_label, cls="detail-value"), cls="detail-row"),
                            Div(Span("Total", cls="detail-label"), Span(f"${booking.total_price}", cls="detail-value price-highlight"), cls="detail-row"),
                            Div(Span("Status", cls="detail-label"), Span(status_label, cls="detail-value status-badge"), cls="detail-row"),
                            cls="booking-details",
                        ),
                        Div(
                            P("Need to check your booking later?", style="margin:0 0 0.5rem; font-size:0.88rem; color:#64748b;"),
                            A("Check Booking Status →", href="/booking/lookup", style="font-size:0.88rem; color:#1a4d6d; font-weight:600;"),
                            style="background:#f8f9fb; border-radius:10px; padding:1rem; margin-bottom:1.5rem; text-align:center;",
                        ),
                        A("Back to Home", href="/", cls="btn btn-primary"),
                        cls="confirmation-card",
                    ),
                    cls="container",
                ),
                cls="confirmation-page",
            ),
            Div(
                Div(
                    Div(
                        Span('✨ New Customer Offer: ', cls='banner-badge'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        
                        Span('✨ New Customer Offer: ', cls='banner-badge', style='margin-left: 2rem;'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        cls='marquee-inner'
                    ),
                    cls='banner-content marquee'
                ),
                cls='announcement-banner',
                style='position: fixed; bottom: 0; left: 0; width: 100%; z-index: 1000;'
            ),
        ),
        lang="en",
    )


async def get_booking_form(request: Request):
    return booking_form_page()


async def post_booking_form(request: Request):
    pool = get_pool()
    form = await request.form()
    try:
        req = CreateBookingRequest(
            customer_name=form.get("customer_name"),
            email=form.get("email"),
            phone=form.get("phone"),
            address=form.get("address"),
            postcode=form.get("postcode"),
            service_date=form.get("service_date"),
            service_time=form.get("service_time"),
            service_type=form.get("service_type"),
            bedrooms=form.get("bedrooms"),
            bathrooms=form.get("bathrooms"),
        )
        booking = await booking_service.create_booking(pool, req)
        return RedirectResponse(f"/booking/{booking.id}", status_code=303)
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return booking_form_page(errors=errors)
    except ValueError as e:
        return booking_form_page(errors={"general": str(e)})


async def get_available_slots(request: Request):
    """JSON endpoint: returns available time slot strings for a given date."""
    date_str = request.query_params.get("date", "")
    try:
        service_date = date_type.fromisoformat(date_str)
    except ValueError:
        return JSONResponse({"slots": []})
    pool = get_pool()
    slots = await availability_service.get_available_slots(pool, service_date)
    # Format as HH:MM:SS strings to match what asyncpg returns
    return JSONResponse({"slots": [f"{s.hour:02d}:{s.minute:02d}:00" for s in slots]})


async def get_booking_confirmation(request: Request):
    booking_id = request.path_params["id"]
    pool = get_pool()
    from repositories import booking_repo
    from uuid import UUID
    booking = await booking_repo.get_by_id(pool, UUID(booking_id))
    if booking is None:
        return Html(Body(H1("Booking not found")))
    return booking_confirmation_page(booking)


LOOKUP_CSS = """
.lookup-page { min-height: 100vh; background: #f8f9fb; padding: 0 0 5rem; }
.lookup-card { background: #fff; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.06); max-width: 540px; margin: 2rem auto 0; }
.lookup-card h1 { font-size: 1.4rem; font-weight: 700; color: #0f2d40; margin: 0 0 0.4rem; }
.lookup-card > p { color: #64748b; font-size: 0.92rem; margin: 0 0 1.75rem; }
.lookup-input { width: 100%; padding: 0.85rem 1rem; border: 2px solid var(--border, #e2e8f0); border-radius: 10px; font-size: 1rem; color: var(--text-dark, #0f172a); box-sizing: border-box; margin-bottom: 1rem; }
.lookup-input:focus { outline: none; border-color: var(--primary, #0f3f5e); }
.lookup-btn { width: 100%; background: var(--primary, #0f3f5e); color: #fff; border: none; padding: 0.85rem; border-radius: 9999px; font-size: 1rem; font-weight: 700; cursor: pointer; }
.lookup-btn:hover { background: var(--primary-light, #1e628f); }
.no-bookings { text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.95rem; }
.booking-card { border: 1.5px solid #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 1rem; }
.booking-card-header { background: #f8f9fb; padding: 0.75rem 1.25rem; display: flex; justify-content: space-between; align-items: center; }
.booking-card-header .svc-name { font-weight: 700; color: #0f2d40; font-size: 0.95rem; }
.status-pill { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-pending_confirmation { background: #fef9c3; color: #854d0e; }
.status-confirmed { background: #dcfce7; color: #166534; }
.status-assigned { background: #dbeafe; color: #1e40af; }
.status-completed { background: #f0fdf4; color: #166534; }
.status-cancelled { background: #fee2e2; color: #991b1b; }
.status-flagged_for_review { background: #fef3c7; color: #92400e; }
.booking-card-body { padding: 0.75rem 1.25rem; }
.booking-meta { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.booking-meta span { font-size: 0.85rem; color: var(--text-light, #64748b); }
.booking-meta strong { color: var(--text-dark, #0f172a); }
.view-link { display: block; text-align: right; font-size: 0.82rem; color: var(--primary, #0f3f5e); font-weight: 600; text-decoration: none; padding: 0.5rem 1.25rem 0.75rem; }
@media (max-width: 600px) {
    .lookup-card { padding: 1.25rem 1rem; }
    .booking-card-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}
"""


def lookup_page(bookings=None, searched=False, email=""):

    results = None
    if searched:
        if not bookings:
            results = Div("No bookings found for that email address.", cls="no-bookings")
        else:
            cards = []
            for b in bookings:
                svc = b.service_type.value.replace("_", " ").title()
                status_val = b.status.value
                status_text = CUSTOMER_STATUS_LABELS.get(status_val, status_val)
                cards.append(
                    Div(
                        Div(
                            Span(svc, cls="svc-name"),
                            Span(status_text, cls=f"status-pill status-{status_val}"),
                            cls="booking-card-header",
                        ),
                        Div(
                            Div(
                                Span(Strong("Date: "), str(b.service_date)),
                                Span(Strong("Total: "), f"${b.total_price}"),
                                Span(Strong("Ref: "), str(b.id)[:8] + "..."),
                                cls="booking-meta",
                            ),
                            cls="booking-card-body",
                        ),
                        A("View full details →", href=f"/booking/{b.id}", cls="view-link"),
                        cls="booking-card",
                    )
                )
            results = Div(*cards)

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Title("Check Booking Status – Filo Cleaning Services"),
            Link(rel="stylesheet", href="/css/styles.css"),
            Style(BOOKING_NAV_CSS),
            Style(LOOKUP_CSS),
        ),
        Body(
            Main(
                booking_nav(right_links=[
                    A("Home", href="/", cls="book-nav-link"),
                    A("Book a Cleaning", href="/book", cls="book-nav-pill"),
                ]),
                Div(
                    Div(
                        H1("Check Your Booking"),
                        P("Enter the email address you used when booking to see your booking status."),
                        Form(
                            Input(type="email", name="email", placeholder="your@email.com",
                                  cls="lookup-input", value=email, required=True),
                            Button("Find My Bookings", type="submit", cls="lookup-btn"),
                            method="POST",
                            action="/booking/lookup",
                        ),
                        results,
                        cls="lookup-card",
                    ),
                    cls="container",
                ),
                cls="lookup-page",
            ),
            Div(
                Div(
                    Div(
                        Span('✨ New Customer Offer: ', cls='banner-badge'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        
                        Span('✨ New Customer Offer: ', cls='banner-badge', style='margin-left: 2rem;'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='/?#quote', cls='banner-link'),
                        cls='marquee-inner'
                    ),
                    cls='banner-content marquee'
                ),
                cls='announcement-banner',
                style='position: fixed; bottom: 0; left: 0; width: 100%; z-index: 1000;'
            ),
        ),
        lang="en",
    )


async def get_lookup(request: Request):
    return lookup_page()


async def post_lookup(request: Request):
    from repositories import booking_repo
    pool = get_pool()
    form = await request.form()
    email = (form.get("email") or "").strip()
    bookings = await booking_repo.get_by_email(pool, email) if email else []
    return lookup_page(bookings=bookings, searched=True, email=email)
