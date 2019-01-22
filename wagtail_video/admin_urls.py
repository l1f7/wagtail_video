from django.conf.urls import url

from wagtail_video.views import chooser, video

urlpatterns = [
    url(r'^$', video.index, name='index'),
    url(r'^add/$', video.add, name='add'),
    url(r'^edit/(\d+)/$', video.edit, name='edit'),
    url(r'^delete/(\d+)/$', video.delete, name='delete'),

    url(r'^chooser/$', chooser.chooser, name='chooser'),
    url(r'^chooser/(\d+)/$', chooser.video_chosen, name='video_chosen'),
    url(r'^usage/(\d+)/$', video.usage, name='video_usage'),
]
