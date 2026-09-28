import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        # Public submission key, intentionally included in the rendered HTML.
        # Override per environment; an explicitly empty value disables signups.
        WEB3FORMS_ACCESS_KEY=os.environ.get(
            "WEB3FORMS_ACCESS_KEY", "a6be62e6-a5a1-462e-9745-5ecff198f102"
        ).strip(),
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
            "img-src 'self'; connect-src https://api.web3forms.com; "
            "form-action https://api.web3forms.com; base-uri 'none'; frame-ancestors 'none'"
        )
        return response

    return app
