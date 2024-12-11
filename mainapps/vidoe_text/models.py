import logging
import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
import logging
import pysrt
import io
import time
from pathlib import Path
from typing import List, Dict
import os
import re
from threading import Timer
from django.core.files import File
from django.conf import settings

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

MAINRESOLUTIONS = {"1:1": 1 / 1, "16:9": 16 / 9, "4:5": 4 / 5, "9:16": 9 / 16}

RESOLUTIONS = {
    "16:9": (1920, 1080),
    "4:3": (1440, 1080),
    "1:1": (1080, 1080),
    # Add other resolutions if needed
}


allow_population_by_field_name = True
populate_by_name = True


def video_file_upload_path(instance, filename):
    """Generate a unique file path for each uploaded text file."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"  # Use UUID to ensure unique file names
    if instance.id:
        return os.path.join("text_files", "new", filename)
    return os.path.join("text_files", filename)


def font_file_upload_path(instance, filename):
    """Generate a unique file path for uploaded custom fonts."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("lead-maker","fonts", filename)


def audio_file_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("audio", filename)


def subriptime_to_seconds(srt_time: pysrt.SubRipTime) -> float:
    return (
        srt_time.hours * 3600
        + srt_time.minutes * 60
        + srt_time.seconds
        + srt_time.milliseconds / 1000.0
    )


class AudioClip(models.Model):
    audio_file = models.FileField(upload_to="lead-editor/audio_clips/")
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds
    voice_id = models.CharField(max_length=255)


class TextFile(models.Model):

    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, editable=False
    )

    video_file = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
    trimmed_video = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
    timestamp_start = models.FloatField(null=True, blank=True)
    timestamp_end = models.FloatField(null=True, blank=True)
    voice_id = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    progress = models.CharField(default="0", max_length=100)
    api_key = models.CharField(max_length=200)
    font_file = models.FileField(upload_to=font_file_upload_path, blank=True, null=True)
    font = models.CharField(max_length=50, blank=True,null=True, default="Arial")
    font_color = models.CharField(max_length=7)  # e.g., hex code: #ffffff
    subtitle_box_color = models.CharField(max_length=7, blank=True, null=True)
    font_size = models.IntegerField()
    resolution=models.CharField(max_length=7, blank=True, null=True) 
    bg_music_text = models.FileField(upload_to="lead-editor/background_txt/", blank=True, null=True)
    audio_file = models.FileField(upload_to="lead-editor/audio_files", blank=True, null=True)
    srt_file = models.FileField(
        upload_to="lead-editor/srt_files/", blank=True, null=True
    )  # SRT file for subtitles
    blank_video = models.FileField(upload_to="lead-editor/blank_video/", blank=True, null=True)
    subtitle_file = models.FileField(upload_to="lead-editor/subtitles/", blank=True, null=True)
    generated_audio = models.FileField(
        upload_to="lead-editor/generated_audio/", blank=True, null=True
    )
    generated_srt = models.FileField(upload_to="lead-editor/generated_srt/", blank=True, null=True)
    generated_blank_video = models.FileField(
        upload_to="lead-editor/generated_blank_video/", blank=True, null=True
    )
    generated_final_video = models.FileField(
        upload_to="lead-editor/generated_final_video/", blank=True, null=True
    )
    generated_watermarked_video = models.FileField(
        upload_to="lead-editor/generated_watermarked_video/", blank=True, null=True
    )
    generated_final_bgm_video = models.FileField(
        upload_to="lead-editor/generated_bgm_video/", blank=True, null=True
    )
    generated_final_bgmw_video = models.FileField(
        upload_to="lead-editor/generated_bgmw_video/", blank=True, null=True
    )

    @staticmethod
    def is_valid_hex_color(color_code):
        """Validate if a color code is a valid hex value."""
        if len(color_code) != 7 or color_code[0] != "#":
            return False
        try:
            int(color_code[1:], 16)
            return True
        except ValueError:
            return False

    def track_progress(self, increase):
        self.progress = str(increase)
        self.save()



def text_clip_upload_path(instance, filename):
    """Generate a unique file path for each uploaded text file."""
    return os.path.join("text_clip", str(instance.text_file.id), filename)


class TextLineVideoClip(models.Model):
    text_file = models.ForeignKey(
        TextFile, on_delete=models.CASCADE, related_name="video_clips"
    )
    text=models.CharField(max_length=100,null=True, blank=True)
    video_file_path = models.FileField(upload_to=text_clip_upload_path,null=True,blank=True)
    line_number = models.IntegerField()
    timestamp_start = models.FloatField(null=True, blank=True)
    timestamp_end = models.FloatField(null=True, blank=True)

    def to_dict(self):
        if self.video_file_path:
            video_path = self.video_file_path 
        else:
            video_path = ""  

        return {
            "line_number": self.line_number,
            "video_path": video_path,  # Return the URL, not the path
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "text":self.text,
        }

    def get_file_status(self):
        if self.video_file_path:
            return "filled"
        else:
            return "empty"

    def get_video_file_name(self):
        filename = self.video_file_path.name.split("/")[-1]

        return filename[:15]

    def __str__(self):
        return f"VideoClip for line {self.line_number} of {self.text_file}"

    class Meta:
        unique_together = ("text_file", "line_number")

        ordering = ["line_number", "text_file"]


class LogoModel(models.Model):
    logo = models.FileField(upload_to="lead-editor/logos/")
