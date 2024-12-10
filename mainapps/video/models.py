import os
import uuid
from django.db import models
from mainapps.accounts.models import User
from .validators import validate_video_file



def video_clip_upload_path(instance, filename):
    """Generate a unique file path for each uploaded text file."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"  # Use UUID to ensure unique file names
    if not instance.id:
        return os.path.join("text_files", "new", filename)
    return os.path.join("video_clip", str(instance.id), filename)


class ClipCategory(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="subcategories",
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        # Ensure the combination of name and user is unique
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_category_per_user"
            )
        ]

    @property
    def get_clip_number(self):
        clips = VideoClip.objects.filter(category=self)
        return len(clips)


class VideoClip(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="user_clips",
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    video_file = models.FileField(
        upload_to=video_clip_upload_path, validators=[validate_video_file]
    )
    duration = models.FloatField(
        null=True, blank=True
    )  # You can extract this with MoviePy when uploading the clip
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        ClipCategory,
        null=True,
        on_delete=models.SET_NULL,
        related_name="video_clips",
        blank=True,
    )
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title or 'Untitled'}"
