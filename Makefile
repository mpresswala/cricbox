format:
	uv run ruff format cricbox

sort:
	uv run ruff check --select I --fix cricbox

lint:
	uv run ruff check cricbox

test:
	DJANGO_SETTINGS_MODULE=cricbox.settings_local uv run python cricbox/manage.py test batsman.tests bowler.tests home.tests match.tests
