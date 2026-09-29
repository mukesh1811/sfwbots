from flask import Blueprint, Response, current_app, render_template

landing = Blueprint("landing", __name__)


@landing.get("/")
def index():
    return render_template(
        "index.html",
        base_url=current_app.config["PUBLIC_BASE_URL"],
        auth_base_url=current_app.config["AUTH_BASE_URL"],
    )


@landing.get("/healthz")
def health():
    return {"status": "ok"}


@landing.get("/robots.txt")
def robots():
    return Response("User-agent: *\nAllow: /\n", mimetype="text/plain")
