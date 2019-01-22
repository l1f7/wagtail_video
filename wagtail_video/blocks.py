from __future__ import unicode_literals

from django.utils.functional import cached_property

from wagtail.core.blocks import ChooserBlock


class VideoChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtail_video.models import get_video_model
        return get_video_model()

    @cached_property
    def widget(self):
        from wagtail_video.widgets import AdminVideoChooser
        return AdminVideoChooser

    def render_basic(self, value):
        raise NotImplementedError('You need to implement %s.render_basic' % self.__class__.__name__)
