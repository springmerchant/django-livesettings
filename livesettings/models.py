from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models, connection, DatabaseError
from django.db.models import loading
from django.utils.translation import ugettext_lazy as _
from keyedcache import cache_key, cache_get, cache_set, NotCachedError
from keyedcache.models import CachedObjectMixin
from livesettings.overrides import get_overrides
import logging

log = logging.getLogger('configuration.models')

__all__ = ['SettingNotSet', 'find_setting']


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


def find_setting(group, key, site=None):
    """Get a setting or longsetting by group and key, cache and return it."""
       
    siteid = _safe_get_siteid(site)
    setting = None
    
    backend = get_overrides(siteid)
    ck = cache_key('Setting', siteid, group, key)
    
    if backend.is_editable:
        setting = backend.get_value(group, key)
    else:
        grp = overrides.get(group, None)
        if grp and grp.has_key(key):
            val = grp[key]
            setting = ImmutableSetting(key=key, group=group, value=val)
            log.debug('Returning overridden: %s', setting)
                
    if not setting:
        raise SettingNotSet(key, cachekey=ck)

    return setting

class SettingNotSet(Exception):    
    def __init__(self, k, cachekey=None):
        self.key = k
        self.cachekey = cachekey
        self.args = [self.key, self.cachekey]

class ImmutableSetting(object):
    
    def __init__(self, group="", key="", value="", site=1):
        self.site = site
        self.group = group
        self.key = key
        self.value = value
        
    def cache_key(self, *args, **kwargs):
        return cache_key('OverrideSetting', self.site, self.group, self.key)
        
    def delete(self):
        pass
        
    def save(self, *args, **kwargs):
        pass
        
    def __repr__(self):
        return "ImmutableSetting: %s.%s=%s" % (self.group, self.key, self.value)