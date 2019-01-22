import json

from django.shortcuts import get_object_or_404, render

from wagtail_video.models import get_video_model
from wagtail_video.permissions import permission_policy

from django.urls import reverse

from wagtail.utils.pagination import paginate
from wagtail.admin.forms import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.utils import PermissionPolicyChecker
from wagtail.admin.utils import popular_tags_for_model
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
    }


def chooser(request):
    Video = get_video_model()

    video_files = []

    if request.user.has_perm('wagtail_video.add_video'):
        can_add = True
    else:
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
        paginator, video_files = paginate(request, video_files, per_page=10)

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

        video_files = Video.objects.order_by('-created_at')
        paginator, video_files = paginate(request, video_files, per_page=10)

    # return render_modal_workflow(request, 'wagtail_video/chooser/chooser.html', None, {
    #     'video_files': video_files,
    #     'searchform': searchform,
    #     'collections': collections,
    #     'is_searching': False,
    # })

    return render_modal_workflow(request, 'wagtail_video/chooser/chooser.html', None,
        template_vars={
            'video_files': video_files,
            'searchform': searchform,
            'is_searching': False,
            'can_add': can_add,
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