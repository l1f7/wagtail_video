from __future__ import absolute_import, unicode_literals

from wagtail_video.widgets import AdminVideoChooser

from wagtail.admin.edit_handlers import BaseChooserPanel


class VideoChooserPanel(BaseChooserPanel):
    object_type_name = 'video'

    def widget_overrides(self):
        return {self.field_name: AdminVideoChooser}
