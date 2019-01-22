from __future__ import absolute_import, unicode_literals

import json

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from wagtail_video.models import get_video_model

from wagtail.admin.widgets import AdminChooser


class AdminVideoChooser(AdminChooser):
    choose_one_text = _('Choose A Video')
    choose_another_text = _('Choose another Video')
    link_to_chosen_text = _('Edit this Video')

    def __init__(self, **kwargs):
        super(AdminVideoChooser, self).__init__(**kwargs)
        self.video_model = get_video_model()

    def render_html(self, name, value, attrs):
        instance, value = self.get_instance_and_id(self.video_model, value)
        original_field_html = super(AdminVideoChooser, self).render_html(name, value, attrs)

        return render_to_string('wagtail_video/widgets/video_chooser.html', {
            'widget': self,
            'original_field_html': original_field_html,
            'attrs': attrs,
            'value': value,
            'video': instance,
        })

    def render_js_init(self, id_, name, value):
        return "createVideoChooser({0});".format(json.dumps(id_))
