import unittest

from app import create_app


class LandingTests(unittest.TestCase):
    def test_waitlist_uses_sign_in_modal_without_an_email_field(self):
        client = create_app({"TESTING": True}).test_client()
        response = client.get("/")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="waitlist-trigger"', page)
        self.assertIn('id="waitlist-dialog"', page)
        self.assertIn("Continue with Google", page)
        self.assertIn("Continue with LinkedIn", page)
        self.assertNotIn('type="email"', page)
        self.assertNotIn("api.web3forms.com", page)

    def test_canonical_and_security_headers(self):
        client = create_app({
            "TESTING": True,
            "PUBLIC_BASE_URL": "https://example.com",
        }).test_client()
        response = client.get("/")
        page = response.get_data(as_text=True)
        self.assertIn('rel="canonical" href="https://example.com/"', page)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertNotIn("web3forms", response.headers["Content-Security-Policy"])

    def test_routes_assets_and_missing_page(self):
        client = create_app({"TESTING": True}).test_client()
        self.assertEqual(client.get("/healthz").json, {"status": "ok"})
        for path in ("/robots.txt", "/static/style.css", "/static/waitlist.js", "/static/favicon.svg"):
            with self.subTest(path=path):
                with client.get(path) as response:
                    self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get("/missing").status_code, 404)


if __name__ == "__main__":
    unittest.main()
