from contextlib import asynccontextmanager
from fasthtml.common import *
from starlette.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from app.routes.marketing import marketing_page
from app.routes.booking import get_booking_form, post_booking_form, get_booking_confirmation, get_lookup, post_lookup
from app.routes.admin import get_admin_login, post_admin_login, get_admin_dashboard, post_update_status, post_admin_logout
from repositories import db
from config import APP_SECRET


@asynccontextmanager
async def lifespan(app):
    await db.init_pool()
    yield
    await db.close_pool()


app, rt = fast_app(static_path='static', lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET)


@rt("/")
def get():
    return marketing_page()


@rt("/manifest.json")
def manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")


@rt("/book")
async def get(request):
    return await get_booking_form(request)


@rt("/book", methods=["POST"])
async def post(request):
    return await post_booking_form(request)


@rt("/booking/lookup")
async def get(request):
    return await get_lookup(request)


@rt("/booking/lookup", methods=["POST"])
async def post(request):
    return await post_lookup(request)


@rt("/booking/{id}")
async def get(request):
    return await get_booking_confirmation(request)


# ── Admin ──
@rt("/admin/login")
async def get(request):
    return await get_admin_login(request)


@rt("/admin/login", methods=["POST"])
async def post(request):
    return await post_admin_login(request)


@rt("/admin")
async def get(request):
    return await get_admin_dashboard(request)


@rt("/admin/bookings/{id}/status", methods=["POST"])
async def post(request):
    return await post_update_status(request)


@rt("/admin/logout", methods=["POST"])
async def post(request):
    return await post_admin_logout(request)


if __name__ == "__main__":
    serve()
