import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from app import create_app


AUTH_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-secret",
    "AUTH_BASE_URL": "https://auth.example",
    "AUTH_LANDING_URL": "https://landing.example/waitlist/",
    "GOOGLE_CLIENT_ID": "google-client",
    "GOOGLE_CLIENT_SECRET": "google-secret",
    "LINKEDIN_CLIENT_ID": "linkedin-client",
    "LINKEDIN_CLIENT_SECRET": "linkedin-secret",
}


class OAuthTests(unittest.TestCase):
    def make_client(self, **overrides):
        return create_app({**AUTH_CONFIG, **overrides}).test_client()

    def oauth_state(self, client, provider):
        with client.session_transaction() as session:
            return session[f"oauth-state:{provider}"]

    def test_provider_requires_credentials(self):
        client = create_app({"TESTING": True}).test_client()
        response = client.get("/auth/google")
        self.assertEqual(response.status_code, 503)

    def test_google_start_redirects_to_google_with_callback_and_state(self):
        client = self.make_client()
        response = client.get("/auth/google")
        location = urlparse(response.headers["Location"])
        query = parse_qs(location.query)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(location.netloc, "accounts.google.com")
        self.assertEqual(query["client_id"], ["google-client"])
        self.assertEqual(query["redirect_uri"], ["https://auth.example/auth/google/callback"])
        self.assertEqual(query["scope"], ["openid email profile"])
        self.assertEqual(query["state"], [self.oauth_state(client, "google")])

    def test_callback_rejects_bad_state(self):
        client = self.make_client()
        client.get("/auth/google")
        response = client.get("/auth/google/callback?code=code&state=wrong")
        self.assertEqual(response.status_code, 400)

    @patch("app.auth._save_waitlist_user")
    @patch("app.auth._get_profile", return_value={"sub": "123", "email": "user@example.com"})
    @patch("app.auth._post_form", return_value={"access_token": "token"})
    def test_callback_saves_waitlist_user_and_returns_to_landing(
        self, post_form, get_profile, save_user
    ):
        client = self.make_client()
        client.get("/auth/google")
        state = self.oauth_state(client, "google")

        response = client.get(f"/auth/google/callback?code=code&state={state}")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "https://landing.example/waitlist/?joined=google")
        post_form.assert_called_once()
        get_profile.assert_called_once_with("https://openidconnect.googleapis.com/v1/userinfo", "token")
        save_user.assert_called_once_with("google", {"sub": "123", "email": "user@example.com"})


if __name__ == "__main__":
    unittest.main()
