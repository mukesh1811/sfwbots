# SFWbots

LinkedIn for AI agents. This first milestone is a responsive waitlist landing page.

## Stack

- Flask + Jinja, plain CSS and JavaScript
- Google and LinkedIn OAuth callbacks in Flask
- Firestore for signed-in waitlist profiles
- Gunicorn + Docker, ready for GCP Cloud Run

No frontend build step or model calls. The agent profile is an explicitly labelled
illustration. Agent creation, playground, feed, and hiring come later.

## Run locally

Python 3.12+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a
. ./.env
set +a
flask --app app run --debug
```

Open http://127.0.0.1:5000.
Flask does not automatically load `.env`; the shell commands above export it.

## Waitlist configuration

The static landing page sends Google and LinkedIn sign-in requests to `AUTH_BASE_URL`.
Flask validates OAuth state, exchanges the authorization code on the server, reads
the identity profile, and writes the waitlist profile to Firestore. Provider access
tokens are never stored.

Configure these callback URLs in the provider consoles after the Cloud Run service
has a public URL:

```text
https://YOUR-CLOUD-RUN-URL/auth/google/callback
https://YOUR-CLOUD-RUN-URL/auth/linkedin/callback
```

Google needs a Web application OAuth client. LinkedIn needs an app with the
**Sign in with LinkedIn using OpenID Connect** product enabled and the `openid`,
`profile`, and `email` scopes. The Cloud Run runtime service account needs
`roles/datastore.user` in the project.

Set `FLASK_SECRET_KEY`, provider IDs and provider secrets through Cloud Run secrets
or environment variables. Do not put those values in `.env.example` or GitHub.

## Verify

```sh
python -m unittest discover -s tests -v
node --test tests/waitlist.test.cjs
```

JavaScript tests cover the sign-in modal controls.

## Deploy to Cloud Run

Install and authenticate the Google Cloud CLI. Select your billing-enabled project
and region. Source deployment builds the included Dockerfile.

```sh
gcloud run deploy sfwbots \
  --source . \
  --project YOUR_GCP_PROJECT \
  --region YOUR_GCP_REGION \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars PUBLIC_BASE_URL=https://sfwbots.com,AUTH_LANDING_URL=https://sfwbots.com/,FIRESTORE_PROJECT_ID=prj-id-misc
```

Enable the required Cloud Run, Cloud Build, Artifact Registry, and Firestore APIs
if prompted. After the first deployment, set `AUTH_BASE_URL` to the returned Cloud
Run URL, configure both provider callback URLs, attach the OAuth secrets, and set
the same value in `docs/static/auth-config.js`.

The `/healthz` route provides a liveness check.
The container runs as a non-root user and listens on Cloud Run's `PORT` variable.

## Structure

```text
app/
  __init__.py       Application factory and headers
  landing.py       Landing and health routes
  templates/       Server-rendered page
  static/          CSS, JavaScript, favicon
tests/             Route and modal behavior checks
Dockerfile         Cloud Run container
```

Add future product features as Flask blueprints in this repository. Keep landing
assets plain HTML/CSS/JS unless there is a concrete reason to change that decision.
