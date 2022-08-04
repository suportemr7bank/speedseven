"""
App settings
"""

from django.conf import settings

# Relative base dir to save templates
TEMPLATE_FOLDER = 'emailtemplates/templates/override/'

TEMPLATE_ABSOLUTE_FOLDER = str(settings.BASE_DIR) + "/" + TEMPLATE_FOLDER
