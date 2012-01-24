"""Allows livesettings to be "locked down" and no longer use the settings page or the database
for settings retrieval.
"""

from django.conf import settings as djangosettings
from django.contrib.sites.models import Site

from livesettings.backends import LiveSettingBackend



import logging

__all__ = ['get_overrides']

def _safe_get_siteid(site):
    if not site:
        try:
            site = Site.objects.get_current()
            siteid = site.id
        except:
            siteid = djangosettings.SITE_ID
    else:
        siteid = site.id
    return siteid

def get_overrides(siteid=-1):
    pass
