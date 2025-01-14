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
from django.utils import timezone

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

MAINRESOLUTIONS = {"1:1": 1 / 1, "16:9": 16 / 9, "4:5": 4 / 5, "9:16": 9 / 16}

RESOLUTIONS = {
    "16:9": (1920, 1080),
    "4:3": (1440, 1080),
    "1:1": (1080, 1080),
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


def text_file_upload_path(instance, filename):
    """Generate a unique file path for each uploaded text file."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"  # Use UUID to ensure unique file names
    if instance.id:
        return os.path.join("text_files", "new", filename)
    return os.path.join("text_files", filename)


# class TextFile(models.Model):

#     user = models.ForeignKey(
#         "accounts.User", on_delete=models.SET_NULL, null=True, editable=False
#     )
#     text_file = models.FileField(upload_to='lead-maker/text_file', null=True, blank=True)
#     video_file = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
#     trimmed_video = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
#     timestamp_start = models.FloatField(null=True, blank=True)
#     timestamp_end = models.FloatField(null=True, blank=True)
#     voice_id = models.CharField(max_length=100)
#     processed = models.BooleanField(default=False)
#     progress = models.CharField(default="0", max_length=100)
#     api_key = models.CharField(max_length=200)
#     font_file = models.FileField(upload_to=font_file_upload_path, blank=True, null=True)
#     font = models.CharField(max_length=50, blank=True,null=True, default="Arial")
#     font_color = models.CharField(max_length=7)  # e.g., hex code: #ffffff
#     subtitle_box_color = models.CharField(max_length=7, blank=True, null=True)
#     font_size = models.IntegerField()
#     resolution=models.CharField(max_length=7, blank=True, null=True) 
#     bg_music_text = models.FileField(upload_to="lead-editor/background_txt/", blank=True, null=True)
#     audio_file = models.FileField(upload_to="lead-editor/audio_files", blank=True, null=True)
#     srt_file = models.FileField(
#         upload_to="lead-editor/srt_files/", blank=True, null=True
#     ) 
#     blank_video = models.FileField(upload_to="lead-editor/blank_video/", blank=True, null=True)
#     subtitle_file = models.FileField(upload_to="lead-editor/subtitles/", blank=True, null=True)
#     generated_audio = models.FileField(
#         upload_to="lead-editor/generated_audio/", blank=True, null=True
#     )
#     generated_srt = models.FileField(upload_to="lead-editor/generated_srt/", blank=True, null=True)
#     generated_blank_video = models.FileField(
#         upload_to="lead-editor/generated_blank_video/", blank=True, null=True
#     )
#     generated_final_video = models.FileField(
#         upload_to="lead-editor/generated_final_video/", blank=True, null=True
#     )
#     generated_watermarked_video = models.FileField(
#         upload_to="lead-editor/generated_watermarked_video/", blank=True, null=True
#     )
#     generated_final_bgm_video = models.FileField(
#         upload_to="lead-editor/generated_bgm_video/", blank=True, null=True
#     )
#     generated_final_bgmw_video = models.FileField(
#         upload_to="lead-editor/generated_bgmw_video/", blank=True, null=True
#     )

#     @staticmethod
#     def is_valid_hex_color(color_code):
#         """Validate if a color code is a valid hex value."""
#         if len(color_code) != 7 or color_code[0] != "#":
#             return False
#         try:
#             int(color_code[1:], 16)
#             return True
#         except ValueError:
#             return False

#     def track_progress(self, increase):
#         self.progress = str(increase)
#         self.save()


class TextFile(models.Model):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, editable=False
    )

    trimmed_video = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
    video_file = models.FileField(upload_to=video_file_upload_path, null=True, blank=True)
    timestamp_start = models.FloatField(null=True, blank=True)
    timestamp_end = models.FloatField(null=True, blank=True)
    text_file = models.FileField(upload_to=text_file_upload_path, null=True, blank=True)
    voice_id = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    progress = models.CharField(default="0", max_length=100)
    api_key = models.CharField(max_length=200)
    resolution = models.CharField(max_length=50,null=True,blank=True)
    font_file = models.FileField(upload_to=font_file_upload_path, blank=True, null=True)
    bg_level = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=9, default=0.1
    )
    font = models.CharField(max_length=50, default="Arial")
    font_color = models.CharField(max_length=7) 
    subtitle_box_color = models.CharField(max_length=7, blank=True, null=True)
    font_size = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    bg_music_text = models.FileField(upload_to="lead_maker/background_txt/", blank=True, null=True)
    audio_file = models.FileField(upload_to="lead_maker/audio_files", blank=True, null=True)
    srt_file = models.FileField(
        upload_to="srt_files/", blank=True, null=True
    )  
    subtitle_file = models.FileField(upload_to="lead_maker/subtitles/", blank=True, null=True)
    subclips_text_file = models.FileField(upload_to="lead_maker/subclips_text_files/", blank=True, null=True)
    blank_video = models.FileField(upload_to="blank_video/", blank=True, null=True)
    generated_audio = models.FileField(
        upload_to="generated_audio/", blank=True, null=True
    )
    generated_subclips_srt = models.FileField(upload_to="lead_maker/generated_subclips_srt/", blank=True, null=True)
    generated_srt = models.FileField(upload_to="lead_maker/generated_srt/", blank=True, null=True)
    generated_blank_video = models.FileField(
        upload_to="lead_maker/generated_blank_video/", blank=True, null=True
    )
    
    generated_final_video = models.FileField(
        upload_to="lead_maker/generated_final_video/", blank=True, null=True
    )
    generated_watermarked_video = models.FileField(
        upload_to="lead_maker/generated_watermarked_video/", blank=True, null=True
    )
    generated_final_bgm_video = models.FileField(
        upload_to="lead_maker/generated_bgm_video/", blank=True, null=True
    )
    generated_final_bgmw_video = models.FileField(
        upload_to="lead_maker/generated_bgmw_video/", blank=True, null=True
    )
    class Meta:
        ordering=['-created_at']
    def get_file_text(self):
        if self.video_clips.all():
            return f'Id: {self.id} -> {self.video_clips.all()[0].slide}'
        return f"Id: {self.id} -> No TexFile added to this Instance"
    def get_clip_number(self):
        total_clips=[]
        for clip in self.video_clips.all() :
            for subclip in clip.subclips.all():
                total_clips.append(subclip)

        return len(total_clips)
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
    def delete(self, using=None, keep_parents=False):
        """Override the delete method to delete associated files."""
        file_fields = [
            "text_file",
            "font_file",
            "bg_music_text",
            "audio_file",
            "srt_file",
            "subtitle_file",
            "subclips_text_file",
            "blank_video",
            "generated_audio",
            "generated_subclips_srt",
            "generated_srt",
            "generated_blank_video",
            "generated_final_video",
            "generated_watermarked_video",
            "generated_final_bgm_video",
            "generated_final_bgmw_video",
        ]

        for field_name in file_fields:
            field = getattr(self, field_name, None)
            if field : 
                if field.name:  # Check if the field is not None and has a file
                    field.delete(save=False)

        super().delete(using=using, keep_parents=keep_parents)


    def track_progress(self, increase):
        self.progress = str(increase)
        self.save()

    def process_text_file(self):
        """Process the uploaded text file and return lines stripped of extra spaces."""
        if not self.text_file:
            raise FileNotFoundError("No text file has been uploaded.")

        try:
            # Using a file-like object for cloud storage systems
            with self.text_file.open("r") as f:
                content = f.read()
                file_obj = io.StringIO(content)
                lines = file_obj.readlines()
            return [line.strip() for line in lines if line.strip()]
        except IOError as e:
            raise IOError(f"Error processing file: {e}")

        return self.voice_id


def text_clip_upload_path(instance, filename):
    """Generate a unique file path for each uploaded text file."""
    return os.path.join("text_clip", str(instance.main_line.id), filename)


# class TextLineVideoClip(models.Model):
#     text_file = models.ForeignKey(
#         TextFile, on_delete=models.CASCADE, related_name="video_clips"
#     )
#     text=models.CharField(max_length=100,null=True, blank=True)
#     video_file_path = models.FileField(upload_to=text_clip_upload_path,null=True,blank=True)
#     line_number = models.IntegerField()
#     timestamp_start = models.FloatField(null=True, blank=True)
#     timestamp_end = models.FloatField(null=True, blank=True)

#     def to_dict(self):
#         if self.video_file_path:
#             video_path = self.video_file_path 
#         else:
#             video_path = ""  

#         return {
#             "line_number": self.line_number,
#             "video_path": video_path,  # Return the URL, not the path
#             "timestamp_start": self.timestamp_start,
#             "timestamp_end": self.timestamp_end,
#             "text":self.text,
#         }

#     def get_file_status(self):
#         if self.video_file_path:
#             return "filled"
#         else:
#             return "empty"

#     def get_video_file_name(self):
#         filename = self.video_file_path.name.split("/")[-1]

#         return filename[:15]

#     def __str__(self):
#         return f"VideoClip for line {self.line_number} of {self.text_file}"

#     class Meta:
#         unique_together = ("text_file", "line_number")

#         ordering = ["line_number", "text_file"]



class TextLineVideoClip(models.Model):
    text_file = models.ForeignKey(
        TextFile, on_delete=models.CASCADE, related_name="video_clips"
    )
    slide=models.CharField(max_length=100,null=True, blank=True)
    remaining=models.CharField(max_length=100,null=True, blank=True)
    line_number = models.IntegerField()
    video_file = models.FileField(upload_to='lead_maker/text_clip_upload_videos/', null=True,blank=True)
    def __str__(self):
        return f"VideoClip for line {self.line_number} of {self.text_file}"
    def get_number_of_subclip(self):
        return len(self.subclips.all())
    class Meta:
        unique_together = ("text_file", "line_number")

        ordering = ["line_number", "text_file"]
    def save(self, *args, **kwargs):
        if not self.line_number:
            max_line_number = (
                TextLineVideoClip.objects.filter(text_file=self.text_file)
                .aggregate(max_line=models.Max('line_number'))['max_line'] or 0
            )
            self.line_number = max_line_number + 1
        super().save(*args, **kwargs)

    def to_dict(self):
         
        if self.video_file:
            video_path = self.video_file  
        else:
            video_path = "" 

        return {
            "video_path": video_path,  
        }
    def delete(self, *args, **kwargs):
        if self.video_file and self.video_file.name:
            self.video_file.delete(save=False)
        super().delete(*args, **kwargs)


class SubClip(models.Model):
    subtittle=models.CharField(max_length=100,)
    
    start = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=6, default=0.1
    )
    end = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=6, default=0.1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    position_in_slide = models.IntegerField(null=True, blank=True)
    video_file = models.FileField(upload_to=text_clip_upload_path)
    main_line=models.ForeignKey(TextLineVideoClip,on_delete=models.CASCADE,related_name='subclips')
    
    def get_video_file_name(self):
        filename=''
        if self.video_file.name:
            filename = self.video_file.name.split("/")[-1]
        return filename[:15]
    def delete(self, *args, **kwargs):
        if self.video_file and self.video_file.name:
            self.video_file.delete(save=False)
        super().delete(*args, **kwargs)
    def save(self, *args, **kwargs):
        if self.main_line and self.main_line.slide:
            try:
                self.position_in_slide = self.main_line.slide.index(self.subtittle)
            except ValueError:
                self.position_in_slide = -1 
        super().save(*args, **kwargs)
    def to_dict(self):
        
        if self.video_file:
            video_path = self.video_file  
        else:
            video_path = "" 

        return {
            "subtittle": self.subtittle,
            "video_path": video_path,  
        }
    class Meta:
        ordering = ['main_line__slide', 'position_in_slide']


class LogoModel(models.Model):
    logo = models.FileField(upload_to="lead-editor/logos/")
