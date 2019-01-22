from django.conf.urls import include, url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from wagtail_video import admin_urls
from wagtail_video.forms import GroupVideoPermissionFormSet
from wagtail_video.models import get_video_model
from wagtail_video.permissions import permission_policy

from django.urls import reverse

from wagtail.admin.menu import MenuItem
from wagtail.admin.search import SearchArea
from wagtail.admin.site_summary import SummaryItem
from wagtail.core import hooks


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^video/', include((admin_urls, 'wagtail_video'), namespace='wagtail_video')),
    ]


class VideoMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_menu_item')
def register_video_menu_item():
    return VideoMenuItem(
        _('Video'),
        reverse('wagtail_video:index'),
        name='media',
        classnames='icon icon-media',
        order=300
    )


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        static('wagtail_video/js/video-chooser.js'),
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}"></script>',
        ((filename, ) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            window.chooserUrls.videoChooser = '{0}';
        </script>
        """,
        reverse('wagtail_video:chooser')
    )


class VideoSummaryItem(SummaryItem):
    order = 300
    template = 'wagtail_video/homepage/site_summary_video.html'

    def get_context(self):
        return {
            'total_video': get_video_model().objects.count(),
        }


@hooks.register('construct_homepage_summary_items')
def add_video_summary_item(request, items):
    items.append(VideoSummaryItem(request))


class VideoSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_search_area')
def register_video_search_area():
    return VideoSearchArea(
        _('Video'),
        reverse('wagtail_video:index'),
        name='video',
        classnames='icon icon-video',
        order=400)


@hooks.register('register_group_permission_panel')
def register_video_permissions_panel():
    return GroupVideoPermissionFormSet


@hooks.register('describe_collection_contents')
def describe_collection_video(collection):
    video_count = get_video_model().objects.filter(collection=collection).count()
    if video_count:
        url = reverse('wagtail_video:index') + ('?collection_id=%d' % collection.id)
        return {
            'count': video_count,
            'count_text': ungettext(
                "%(count)s video file",
                "%(count)s video files",
                video_count
            ) % {'count': video_count},
            'url': url,
        }
