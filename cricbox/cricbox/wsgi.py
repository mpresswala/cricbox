"""
WSGI config for cricbox project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

# Standard imports
import os
import sys

# Django imports
from django.core.wsgi import get_wsgi_application

cricbox_path = os.environ.get("DJANGO_CRICBOX_PATH")
if cricbox_path:
    sys.path.append(cricbox_path)
application = get_wsgi_application()
