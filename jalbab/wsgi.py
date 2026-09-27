"""
WSGI config for jalbab project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jalbab.settings')

application = get_wsgi_application()

# Vercel يدعم كلا الاسمين
app = application