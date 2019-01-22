from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import Signal
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from taggit.managers import TaggableManager

from wagtail.admin.utils import get_object_usage
from wagtail.core.models import CollectionMember
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

class VideoQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


@python_2_unicode_compatible
class AbstractVideo(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    mp4 = models.FileField(upload_to='video', verbose_name=_('mp4'))
    ogg = models.FileField(upload_to='video', blank=True, verbose_name=_('ogg'))
    webm = models.FileField(upload_to='video', blank=True, verbose_name=_('webm'))

    thumbnail = models.FileField(upload_to='video_thumbnails', blank=True, verbose_name=_('thumbnail'))

    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('uploaded by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('tags'))

    objects = VideoQuerySet.as_manager()

    search_fields = CollectionMember.search_fields + [
        index.SearchField('title', partial_match=True, boost=10),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('uploaded_by_user'),
    ]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.mp4.name)

    @property
    def thumbnail_filename(self):
        return os.path.basename(self.thumbnail.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1][1:]

    @property
    def mp4_url(self):
        return self.mp4.url

    @property
    def ogg_url(self):
        return self.ogg.url
    
    @property
    def webm_url(self):
        return self.webm.url

    @property
    def thumbnail_url(self):
        return self.thumbnail.url

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtail_video:video_usage',
                       args=(self.id,))

    def is_editable_by_user(self, user):
        from wagtail_video.permissions import permission_policy
        return permission_policy.user_has_permission_for_instance(user, 'change', self)

    class Meta:
        abstract = True
        verbose_name = _('video')


class Video(AbstractVideo):
    admin_form_fields = (
        'title',
        'mp4',
        'ogg',
        'webm',
        'collection',
        'thumbnail',
        'tags',
    )


def get_video_model():
    from django.conf import settings
    from django.apps import apps

    try:
        app_label, model_name = settings.WAGTAILVIDEO_VIDEO_MODEL.split('.')
    except AttributeError:
        return Video
    except ValueError:
        raise ImproperlyConfigured("WAGTAILVIDEO_VIDEO_MODEL must be of the form 'app_label.model_name'")

    video_model = apps.get_model(app_label, model_name)
    if video_model is None:
        raise ImproperlyConfigured(
            "WAGTAILVIDEO_VIDEO_MODEL refers to model '%s' that has not been installed" %
            settings.WAGTAILVIDEO_VIDEO_MODEL
        )
    return video_model


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Video)
def video_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.mp4.delete(False)
    instance.ogg.delete(False)
    instance.webm.delete(False)
    instance.thumbnail.delete(False)


video_served = Signal(providing_args=['request'])
