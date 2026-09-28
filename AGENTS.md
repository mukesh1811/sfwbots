# Collaboration

Be blunt, keep it short, and challenge my assumptions

Do not start coding until the user says DO. Once authorized, finish the agreed task.

# Product

SFWbots is a professional network for AI agents. People create an agent, give it
skills and experience in a playground, then let it show its work, build a
reputation, and eventually get hired. Training means instructions, memory, and
tools, not updating model weights. Hiring is a later milestone.

# Current scope

Waitlist landing page only. One Flask application, server-rendered HTML, plain CSS,
and vanilla JavaScript. GCP Cloud Run is the intended host. Web3Forms delivers
signup notifications; no database is needed for this milestone.

Use a serious professional network aesthetic: white cards, a light grey canvas,
system typography, thin borders, and electric cyan #00D4FF. Buttons use dark text
on cyan. No fake live metrics, testimonials, or working product controls.

Never report signup success without confirmation from Web3Forms. Keep the form
disabled when its access key is missing. Do not commit credentials or .env files.

# Verification

Run `python -m unittest discover -s tests -v` and `node --test tests/waitlist.test.cjs`.
Check desktop and mobile layouts after visual changes. Never send real test
emails without authorization.
