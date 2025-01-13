from django.urls import path,re_path
from . import views

app_name = "video_text"
urlpatterns = [
    path("", views.add_text_video, name="add_text"),
    path("add-leads/<str:textfile_id>/", views.add_leads, name="add_leads"),
    path("trim-video/<str:textfile_id>/", views.trim_video, name="trim_video"),
    path("download_video/<str:textfile_id>/", views.download_video, name="download_video"),
    path(
        "progress_page/<str:al_the_way>/<str:text_file_id>",
        views.progress_page,
        name="progress_page",
    ),
    path("add_text_clip_line/<str:textfile_id>/", views.add_text_clip_line, name="add_text_clip_line"),
    path("edit_text_clip_line/<str:textfile_id>/", views.edit_text_clip_line, name="edit_text_clip_line"),
    path("progress/<str:text_file_id>/", views.progress, name="progress"),
    path(
        "process-background-music/<str:textfile_id>/",
        views.process_background_music,
        name="process_background_music",
    ),
    path("media/<str:file_name>/", views.serve_file, name="serve_file"),
    re_path(
        r"^media/(?P<file_key>.+)/(?P<textfile_id>\w+)/$",
        views.download_file_from_s3,
        name="download_file",
    ),
    re_path(r"^media/(?P<file_key>.+)/$", views.download_file_from_s3, name="download_file_"),
    path(
        "delete-background-music/<int:id>/",
        views.delete_background_music,
        name="delete_background_music",
    ),
    path(
        "delete-clip/<int:id>/",
        views.delete_clip,
        name="delete_clip",
    ),
    path("validate_api_key/", views.validate_api_keyv, name="validate_api_key"),
    # path("validate_api_key/", views.validate_api_keyv, name="validate_api_key"),

]
