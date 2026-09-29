import os
import secrets

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    app = Flask(__name__)
    flask_secret_key = os.environ.get("FLASK_SECRET_KEY", "").strip()
    app.config.from_mapping(
        SECRET_KEY=flask_secret_key or secrets.token_urlsafe(32),
        FLASK_SECRET_KEY_CONFIGURED=bool(flask_secret_key),
        PUBLIC_BASE_URL=os.environ.get("PUBLIC_BASE_URL", "https://sfwbots.com").rstrip("/"),
        AUTH_BASE_URL=os.environ.get("AUTH_BASE_URL", "").rstrip("/"),
        AUTH_LANDING_URL=os.environ.get(
            "AUTH_LANDING_URL", "https://mukesh1811.github.io/sfwbots/"
        ),
        FIRESTORE_PROJECT_ID=os.environ.get("FIRESTORE_PROJECT_ID", "").strip(),
        FIRESTORE_COLLECTION=os.environ.get("FIRESTORE_COLLECTION", "waitlist_users").strip(),
        GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID", "").strip(),
        GOOGLE_CLIENT_SECRET=os.environ.get("GOOGLE_CLIENT_SECRET", "").strip(),
        GOOGLE_REDIRECT_URI=os.environ.get("GOOGLE_REDIRECT_URI", "").strip(),
        LINKEDIN_CLIENT_ID=os.environ.get("LINKEDIN_CLIENT_ID", "").strip(),
        LINKEDIN_CLIENT_SECRET=os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip(),
        LINKEDIN_REDIRECT_URI=os.environ.get("LINKEDIN_REDIRECT_URI", "").strip(),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    from .auth import auth
    from .landing import landing

    app.register_blueprint(auth)
    app.register_blueprint(landing)

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        return response

    return app
