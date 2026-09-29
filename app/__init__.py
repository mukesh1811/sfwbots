import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        PUBLIC_BASE_URL=os.environ.get("PUBLIC_BASE_URL", "https://sfwbots.com").rstrip("/"),
    )
    if test_config:
        app.config.update(test_config)

    from .landing import landing

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
