from fasthtml.common import *
from starlette.responses import FileResponse
from app.routes.marketing import marketing_page

app, rt = fast_app(static_path='static')


@rt("/")
def get():
    return marketing_page()


@rt("/manifest.json")
def manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")


if __name__ == "__main__":
    serve()
