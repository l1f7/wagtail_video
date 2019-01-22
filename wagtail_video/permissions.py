from wagtail.core.permission_policies.collections import CollectionOwnershipPermissionPolicy

from wagtail_video.models import Video, get_video_model

permission_policy = CollectionOwnershipPermissionPolicy(
    get_video_model(),
    auth_model=Video,
    owner_field_name='uploaded_by_user'
)
