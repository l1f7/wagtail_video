from django.conf import settings
from django.contrib import admin

from wagtail_video.models import Video

if hasattr(settings, 'WAGTAILVIDEO_VIDEO_MODEL') and settings.WAGTAILVIDEO_VIDEO_MODEL != 'wagtail_video.Video':
    # This installation provides its own custom video class;
    # to avoid confusion, we won't expose the unused wagtail_video.Video class
    # in the admin.
    pass
else:
    admin.site.register(Video)
