from starlette.requests import Request
from starlette.responses import RedirectResponse


def is_admin(request: Request) -> bool:
    return request.session.get("admin") is True


def require_admin(request: Request):
    """Returns a redirect if not authenticated, else None."""
    if not is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    return None
