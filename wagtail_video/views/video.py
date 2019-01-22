from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers

from wagtail_video.forms import get_video_form
from wagtail_video.models import get_video_model
from wagtail_video.permissions import permission_policy

from django.urls import reverse

from wagtail.utils.pagination import paginate
from wagtail.admin import messages
from wagtail.admin.forms import SearchForm
from wagtail.admin.utils import (
    PermissionPolicyChecker, permission_denied, popular_tags_for_model
)
from wagtail.core.models import Collection
from wagtail.search.backends import get_search_backends

from wagtail.admin.edit_handlers import FieldPanel

permission_checker = PermissionPolicyChecker(permission_policy)


@permission_checker.require_any('add', 'change', 'delete')
@vary_on_headers('X-Requested-With')
def index(request):
    Video = get_video_model()

    # Get video files (filtered by user permission)
    video = permission_policy.instances_user_has_any_permission_for(
        request.user, ['change', 'delete']
    )

    # Ordering
    if 'ordering' in request.GET and request.GET['ordering'] in ['title', '-created_at']:
        ordering = request.GET['ordering']
    else:
        ordering = '-created_at'
    video = video.order_by(ordering)

    # Filter by collection
    current_collection = None
    collection_id = request.GET.get('collection_id')
    if collection_id:
        try:
            current_collection = Collection.objects.get(id=collection_id)
            video = video.filter(collection=current_collection)
        except (ValueError, Collection.DoesNotExist):
            pass

    # Search
    query_string = None
    if 'q' in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search video files"))
        if form.is_valid():
            query_string = form.cleaned_data['q']
            video = video.search(query_string)
    else:
        form = SearchForm(placeholder=_("Search video"))

    # Pagination
    paginator, video = paginate(request, video)

    collections = permission_policy.collections_user_has_any_permission_for(
        request.user, ['add', 'change']
    )
    if len(collections) < 2:
        collections = None

    # Create response
    if request.is_ajax():
        return render(request, 'wagtail_video/video/results.html', {
            'ordering': ordering,
            'video_files': video,
            'query_string': query_string,
            'is_searching': bool(query_string),
        })
    else:
        return render(request, 'wagtail_video/video/index.html', {
            'ordering': ordering,
            'video_files': video,
            'query_string': query_string,
            'is_searching': bool(query_string),

            'search_form': form,
            'popular_tags': popular_tags_for_model(Video),
            'user_can_add': permission_policy.user_has_permission(request.user, 'add'),
            'collections': collections,
            'current_collection': current_collection,
        })


@permission_checker.require('add')
def add(request):
    Video = get_video_model()
    VideoForm = get_video_form(Video)

    if request.POST:
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(request.POST, request.FILES, instance=video, user=request.user)
        if form.is_valid():
            form.save()

            # Reindex the video entry to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(video)

            messages.success(request, _("Video file '{0}' added.").format(video.title), buttons=[
                messages.button(reverse('wagtail_video:edit', args=(video.id,)), _('Edit'))
            ])
            return redirect('wagtail_video:index')
        else:
            messages.error(request, _("The video file could not be saved due to errors."))
    else:
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(user=request.user, instance=video)

    return render(request, "wagtail_video/video/add.html", {
        'form': form,
    })


@permission_checker.require('change')
def edit(request, video_id):
    Video = get_video_model()
    VideoForm = get_video_form(Video)

    video = get_object_or_404(Video, id=video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, 'change', video):
        return permission_denied(request)

    if request.POST:
        original_file = video.mp4
        form = VideoForm(request.POST, request.FILES, instance=video, user=request.user)
        if form.is_valid():
            if 'file' in form.changed_data:
                # if providing a new video file, delete the old one.
                # NB Doing this via original_file.delete() clears the file field,
                # which definitely isn't what we want...
                original_file.storage.delete(original_file.name)
            video = form.save()

            # Reindex the video entry to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(video)

            messages.success(request, _("Video file '{0}' updated").format(video.title), buttons=[
                messages.button(reverse('wagtail_video:edit', args=(video.id,)), _('Edit'))
            ])
            return redirect('wagtail_video:index')
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = VideoForm(instance=video, user=request.user)

    filesize = None

    # Get file size when there is a file associated with the Video object
    if video.mp4:
        try:
            filesize = video.mp4.size
        except OSError:
            # File doesn't exist
            pass

    if video.ogg:
        try:
            filesize = video.ogg.size
        except OSError:
            # File doesn't exist
            pass

    if video.webm:
        try:
            filesize = video.webm.size
        except OSError:
            # File doesn't exist
            pass

    if not filesize:
        messages.error(
            request,
            _("The file could not be found. Please change the source or delete the video file"),
            buttons=[messages.button(reverse('wagtail_video:delete', args=(video.id,)), _('Delete'))]
        )

    return render(request, "wagtail_video/video/edit.html", {
        'video': video,
        'filesize': filesize,
        'form': form,
        'user_can_delete': permission_policy.user_has_permission_for_instance(
            request.user, 'delete', video
        ),
    })


@permission_checker.require('delete')
def delete(request, video_id):
    Video = get_video_model()
    video = get_object_or_404(Video, id=video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, 'delete', video):
        return permission_denied(request)

    if request.POST:
        video.delete()
        messages.success(request, _("Video file '{0}' deleted.").format(video.title))
        return redirect('wagtail_video:index')

    return render(request, "wagtail_video/video/confirm_delete.html", {
        'video': video,
    })


def usage(request, video_id):
    Video = get_video_model()
    video = get_object_or_404(Video, id=video_id)

    paginator, used_by = paginate(request, video.get_usage())

    return render(request, "wagtail_video/video/usage.html", {
        'video': video,
        'used_by': used_by
    })
