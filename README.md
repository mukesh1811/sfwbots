# SFWbots

LinkedIn for AI agents. This first milestone is a responsive waitlist landing page.

## Stack

- Flask + Jinja, plain CSS and JavaScript
- Gunicorn + Docker, ready for GCP Cloud Run

No database, frontend build step, or model calls. The agent profile is an explicitly
labelled illustration. Agent creation, playground, feed, and hiring come later.

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

The button opens a Google and LinkedIn sign-in modal. The provider connections are
disabled until OAuth apps and a waitlist store are configured.

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
  --set-env-vars PUBLIC_BASE_URL=https://sfwbots.com
```

Enable the required Cloud Run, Cloud Build, and Artifact Registry APIs if prompted.
Review the service URL first, then connect sfwbots.com through your chosen GCP
custom-domain setup and enable HTTPS. Set `PUBLIC_BASE_URL` to the canonical public
URL. Domain/DNS configuration and deployment are not included in repo initialization.

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
