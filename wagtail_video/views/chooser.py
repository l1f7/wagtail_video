import json

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.models import popular_tags_for_model
from wagtail.search.backends import get_search_backends

from wagtail_video.forms import get_video_form
from wagtail_video.models import get_video_model
from wagtail_video.permissions import permission_policy

from django.urls import reverse

from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.core.models import Collection

permission_checker = PermissionPolicyChecker(permission_policy)


def get_video_json(video):
    """
    helper function: given a video, return the json to pass back to the
    chooser panel
    """

    return json.dumps({
        'id': video.id,
        'title': video.title,
        'edit_link': reverse('wagtail_video:edit', args=(video.id,)),
        'mp4_url': video.mp4_url if video.mp4 else None
    })


def get_video_result_data(video):
    """
    helper function: given an video file, return the json data to pass back to the
    video chooser panel
    """
    return {
        'id': video.id,
        'edit_link': reverse('wagtail_video:edit', args=(video.id,)),
        'title': video.title,
        'mp4_url': video.mp4_url if video.mp4 else None
    }


def chooser(request):
    Video = get_video_model()

    video_files = []

    if request.user.has_perm('wagtail_video.add_video'):
        can_add = True
        VideoForm = get_video_form(Video)
        video = Video(uploaded_by_user=request.user)
        uploadform = VideoForm(user=request.user, instance=video)
    else:
        uploadform = None
        can_add = False

    q = None
    is_searching = False
    if 'q' in request.GET or 'p' in request.GET:
        video_files = Video.objects.all()

        collection_id = request.GET.get('collection_id')
        if collection_id:
            video_files = video_files.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            video_files = video_files.search(q)
            is_searching = True
        else:
            video_files = video_files.order_by('-created_at')
            is_searching = False

        # Pagination
        paginator = Paginator(video_files, per_page=10)
        video_files = paginator.get_page(request.GET.get('p'))

        return render(request, "wagtail_video/chooser/results.html", {
            'video_files': video_files,
            'query_string': q,
            'is_searching': is_searching,
        })
    else:
        searchform = SearchForm()

        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None
        else:
            collections = Collection.order_for_display(collections)

        video_files = Video.objects.order_by('-created_at')
        paginator = Paginator(video_files, per_page=10)
        video_files = paginator.get_page(request.GET.get('p'))

    # return render_modal_workflow(request, 'wagtail_video/chooser/chooser.html', None, {
    #     'video_files': video_files,
    #     'searchform': searchform,
    #     'collections': collections,
    #     'is_searching': False,
    # })

    return render_modal_workflow(
        request,
        'wagtail_video/chooser/chooser.html',
        None,
        template_vars={
            'collections': collections,
            'video_files': video_files,
            'searchform': searchform,
            'is_searching': False,
            'can_add': can_add,
            'uploadform': uploadform,
            'query_string': q,
            'popular_tags': popular_tags_for_model(Video),
        },
        json_data={
            'step': 'chooser',
        }
     )


# def video_chosen(request, video_id):
#     video = get_object_or_404(get_video_model(), id=video_id)
#     json_data = get_video_json(video)
#     json_data['step'] = 'video_chosen'
#     return render_modal_workflow(
#         request,
#         None,
#         None, #'wagtail_video/chooser/video_chosen.js',
#         json_data=json_data
#     )

def video_chosen(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    return render_modal_workflow(
        request, None, None,
        None, json_data={'step': 'video_chosen', 'result': get_video_result_data(video)}
    )


@permission_checker.require('add')
def chooser_upload(request):
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

            return render_modal_workflow(
                request, None, None,
                None, json_data={'step': 'video_chosen', 'result': get_video_result_data(video)}
            )
    else:
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(user=request.user, instance=video)

    video_files = Video.objects.order_by('-created_at')
    paginator = Paginator(video_files, per_page=10)
    video_files = paginator.get_page(request.GET.get('p'))

    context = {
        'video_files': video_files,
        'searchform': SearchForm(),
        'is_searching': False,
        'can_add': True,
        'uploadform': form,
        'popular_tags': popular_tags_for_model(Video),
    }

    return render_modal_workflow(
        request, 'wagtailimages/chooser/chooser.html', None, context,
        json_data={
            'step': 'chooser',
        }
    )
