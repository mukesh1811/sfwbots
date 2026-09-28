import unittest

from app import create_app


class LandingTests(unittest.TestCase):
    def test_unconfigured_form_is_honest_and_disabled(self):
        client = create_app({"TESTING": True, "WEB3FORMS_ACCESS_KEY": ""}).test_client()
        response = client.get("/")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data-configured="false"', page)
        self.assertIn('type="submit" disabled', page)
        self.assertIn("Signups aren’t open yet", page)

    def test_configured_key_is_escaped_and_form_enabled(self):
        client = create_app({
            "TESTING": True,
            "WEB3FORMS_ACCESS_KEY": 'key"><script>alert(1)</script>',
            "PUBLIC_BASE_URL": "https://example.com",
        }).test_client()
        response = client.get("/")
        page = response.get_data(as_text=True)
        self.assertIn('data-configured="true"', page)
        self.assertNotIn('type="submit" disabled', page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn('rel="canonical" href="https://example.com/"', page)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

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
