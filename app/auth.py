from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from flask import Blueprint, abort, current_app, redirect, request, session, url_for


auth = Blueprint("auth", __name__, url_prefix="/auth")

PROVIDERS = {
    "google": {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
    },
    "linkedin": {
        "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/userinfo",
        "scope": "openid profile email",
    },
}


class OAuthFailure(RuntimeError):
    pass


@auth.get("/<provider>")
def start(provider):
    provider_config = _provider_config(provider)
    state = secrets.token_urlsafe(32)
    session[_state_key(provider)] = state

    params = {
        "response_type": "code",
        "client_id": provider_config["client_id"],
        "redirect_uri": _callback_url(provider),
        "scope": provider_config["scope"],
        "state": state,
    }
    if provider == "google":
        params["prompt"] = "select_account"
    return redirect(f"{provider_config['authorization_url']}?{urlencode(params)}")


@auth.get("/<provider>/callback")
def callback(provider):
    provider_config = _provider_config(provider)
    expected_state = session.pop(_state_key(provider), "")
    returned_state = request.args.get("state", "")
    if not expected_state or not hmac.compare_digest(expected_state, returned_state):
        abort(400, description="Invalid OAuth state.")

    if request.args.get("error"):
        return _landing_redirect(auth_error=provider)

    code = request.args.get("code")
    if not code:
        abort(400, description="OAuth provider did not return a code.")

    try:
        tokens = _post_form(
            provider_config["token_url"],
            {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": provider_config["client_id"],
                "client_secret": provider_config["client_secret"],
                "redirect_uri": _callback_url(provider),
            },
        )
        access_token = tokens.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise OAuthFailure("Provider did not return an access token.")
        profile = _get_profile(provider_config["userinfo_url"], access_token)
        _save_waitlist_user(provider, profile)
    except OAuthFailure:
        current_app.logger.exception("OAuth callback failed for %s", provider)
        return _landing_redirect(auth_error=provider)

    return _landing_redirect(joined=provider)


def _provider_config(provider):
    definition = PROVIDERS.get(provider)
    if definition is None:
        abort(404)

    prefix = provider.upper()
    client_id = current_app.config.get(f"{prefix}_CLIENT_ID", "")
    client_secret = current_app.config.get(f"{prefix}_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        abort(503, description=f"{provider.title()} sign-in is not configured.")
    if not current_app.testing and not current_app.config["FLASK_SECRET_KEY_CONFIGURED"]:
        abort(503, description="Sign-in is not configured.")

    return {**definition, "client_id": client_id, "client_secret": client_secret}


def _callback_url(provider):
    configured = current_app.config.get(f"{provider.upper()}_REDIRECT_URI", "")
    if configured:
        return configured
    auth_base_url = current_app.config.get("AUTH_BASE_URL", "").rstrip("/")
    if auth_base_url:
        return f"{auth_base_url}/auth/{provider}/callback"
    return url_for("auth.callback", provider=provider, _external=True)


def _state_key(provider):
    return f"oauth-state:{provider}"


def _landing_redirect(**query_updates):
    parts = urlsplit(current_app.config["AUTH_LANDING_URL"])
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update(query_updates)
    return redirect(urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)))


def _post_form(url, values):
    return _request_json(
        url,
        data=urlencode(values).encode(),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )


def _get_profile(url, access_token):
    return _request_json(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {access_token}"},
    )


def _request_json(url, *, data=None, headers=None):
    request_headers = {"Accept": "application/json", **(headers or {})}
    request_object = Request(url, data=data, headers=request_headers)
    try:
        with urlopen(request_object, timeout=10) as response:
            payload = response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise OAuthFailure("OAuth provider request failed.") from error

    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise OAuthFailure("OAuth provider returned invalid JSON.") from error
    if not isinstance(decoded, dict):
        raise OAuthFailure("OAuth provider returned an invalid response.")
    return decoded


def _save_waitlist_user(provider, profile):
    subject = profile.get("sub")
    if not isinstance(subject, str) or not subject:
        raise OAuthFailure("OAuth provider did not return a user identifier.")

    try:
        from google.cloud import firestore

        database = firestore.Client(project=current_app.config.get("FIRESTORE_PROJECT_ID") or None)
        user_id = hashlib.sha256(f"{provider}:{subject}".encode()).hexdigest()
        user_ref = database.collection(current_app.config["FIRESTORE_COLLECTION"]).document(user_id)
        now = datetime.now(timezone.utc)
        record = {
            "provider": provider,
            "provider_subject": subject,
            "name": _string_or_none(profile.get("name")),
            "email": _string_or_none(profile.get("email")),
            "email_verified": profile.get("email_verified") is True,
            "picture": _string_or_none(profile.get("picture")),
            "updated_at": now,
        }
        if not user_ref.get().exists:
            record["joined_at"] = now
        user_ref.set(record, merge=True)
    except Exception as error:
        raise OAuthFailure("Could not save waitlist user.") from error


def _string_or_none(value):
    return value if isinstance(value, str) and value else None
