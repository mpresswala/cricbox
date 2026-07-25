format:
	uv run black cricbox

sort:
	uv run isort cricbox

lint:
	uv run flake8 cricbox

test:
	DJANGO_SETTINGS_MODULE=cricbox.settings_local uv run python cricbox/manage.py test batsman.tests bowler.tests home.tests
