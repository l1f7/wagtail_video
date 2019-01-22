from __future__ import unicode_literals

from django import forms
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _

from wagtail_video.models import Video
from wagtail_video.permissions import \
    permission_policy as video_permission_policy

from wagtail.admin import widgets
from wagtail.admin.forms import (
    BaseCollectionMemberForm, collection_member_permission_formset_factory
)

class BaseVideoForm(BaseCollectionMemberForm):
    permission_policy = video_permission_policy

    def __init__(self, *args, **kwargs):
        super(BaseVideoForm, self).__init__(*args, **kwargs)


def get_video_form(model):
    fields = model.admin_form_fields
    if 'collection' not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # video to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ['collection']

    return modelform_factory(
        model,
        form=BaseVideoForm,
        fields=fields,
        widgets={
            'tags': widgets.AdminTagWidget,
            'file': forms.FileInput(),
            'thumbnail': forms.ClearableFileInput(),
        })


GroupVideoPermissionFormSet = collection_member_permission_formset_factory(
    Video,
    [
        ('add_video', _("Add"), _("Add/edit video you own")),
        ('change_video', _("Edit"), _("Edit any video")),
    ],
    'wagtail_video/permissions/includes/video_permissions_formset.html'
)
