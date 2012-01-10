from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.encoding import force_unicode
from livesettings import ConfigurationSettings, forms
from livesettings.overrides import get_overrides
import django
import logging

log = logging.getLogger('livesettings.views')

def _pre_12():
    ver = django.VERSION
    return ver[0] == 1 and ver[1] < 2

@csrf_protect
def group_settings(request, group, template='livesettings/group_settings.html'):
    mgr = ConfigurationSettings()
    if group is None:
        settings = mgr
        title = 'Site settings'
    else:
        settings = mgr[group]
        title = settings.name
        log.debug('title: %s', title)

    if True:
        # Create an editor customized for the current user
        #editor = forms.customized_editor(settings)

        if request.method == 'POST':
            # Populate the form with user-submitted data
            data = request.POST.copy()
            form = forms.SettingsEditor(data, settings=settings)
            if form.is_valid():
                form.full_clean()
                for name, value in form.cleaned_data.items():
                    group, key = name.split('__')
                    cfg = mgr.get_config(group, key)
                    if cfg.update(value):

                        # Give user feedback as to which settings were changed
                        messages.add_message(request, messages.INFO, 'Updated %s - %s' % (force_unicode(cfg.group.name), force_unicode(cfg.description)))

                return HttpResponseRedirect(request.path)
        else:
            # Leave the form populated with current setting values
            #form = editor()
            form = forms.SettingsEditor(settings=settings)
    else:
        form = None

    return render_to_response(template, {
        'title': title,
        'group' : group,
        'form': form,
        'use_db' : True,
        'DJANGO_PRE_12' : _pre_12()
    }, context_instance=RequestContext(request))

group_settings = never_cache(permission_required('livesettings.change_setting')(group_settings))

# Site-wide setting editor is identical, but without a group
# permission_required is implied, since it calls group_settings
def site_settings(request):
    return group_settings(request, group=None, template='livesettings/site_settings.html')

def export_as_python(request):
    """Export site settings as a dictionary of dictionaries"""

    from livesettings.models import Setting, LongSetting
    import pprint

    work = {}
    both = list(Setting.objects.all())
    both.extend(list(LongSetting.objects.all()))

    for s in both:
        sitesettings = work.setdefault(s.site.id, {'DB': False, 'SETTINGS':{}})['SETTINGS']
        sitegroup = sitesettings.setdefault(s.group, {})
        sitegroup[s.key] = s.value

    pp = pprint.PrettyPrinter(indent=4)
    pretty = pp.pformat(work)

    return render_to_response('livesettings/text.txt', { 'text' : pretty }, mimetype='text/plain')

# Required permission `is_superuser` is equivalent to auth.change_user,
# because who can modify users, can easy became a superuser.
export_as_python = never_cache(permission_required('auth.change_user')(export_as_python))
