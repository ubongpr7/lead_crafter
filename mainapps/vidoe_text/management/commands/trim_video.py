from mainapps.vidoe_text.models import LogoModel, TextFile
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)
import os
import sys
import json
import moviepy.video.fx.all as vfx
from moviepy.config import change_settings
from django.core.management.base import BaseCommand
from moviepy.editor import TextClip
import os
import tempfile
import logging
from moviepy.editor import AudioFileClip

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

from moviepy.editor import VideoFileClip, ImageClip
import numpy as np


import tempfile
from django.core.files.base import ContentFile

import time
from django.utils import timezone
from django.conf import settings
import boto3

base_path = settings.MEDIA_ROOT


# Set the path to ImageMagick executable
imagemagick_path = "convert"
os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path
change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
bucket_name = settings.AWS_STORAGE_BUCKET_NAME
aws_secret = settings.AWS_SECRET_ACCESS_KEY
s3 = boto3.client(
    "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=aws_secret
)


def download_from_s3(file_key, local_file_path):
    """
    Download a file from S3 and save it to a local path.

    Args:
        file_key (str): The S3 object key (file path in the bucket).
        local_file_path (str): The local file path where the file will be saved.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Download the file from the bucket using its S3 object key
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        object_content = response["Body"].read()
        logging.info(f"Downloaded {file_key} from S3 to {local_file_path}")
        return object_content
    except Exception as e:
        logging.error(f"Failed to download {file_key} from S3: {e}")
        return False


def update_progress(progress, dir_s):
    with open(dir_s, "w") as f:
        f.write(str(progress))


class Command(BaseCommand):
    help = "Process video files based on TextFile model"

    def add_arguments(self, parser):
        parser.add_argument("text_file_id", type=int)

    def handle(self, *args, **kwargs):
        text_file_id = kwargs["text_file_id"]
        self.text_file_instance = TextFile.objects.get(id=text_file_id)
        
        self.text_file_instance.track_progress(5)


        self.trim_video_()
        self.stdout.write(
            self.style.SUCCESS(f"Processing complete for {text_file_id}.")
        )

    def load_video_from_instance(self, file_field) -> VideoFileClip:
        """
        Load a video from the specified file field in the text_file_instance, downloading it from S3,
        and return it as a MoviePy VideoFileClip.

        Args:
            text_file_instance: An instance containing the S3 path for the video file.
            file_field: The name of the file field in text_file_instance that holds the video.

        Returns:
            VideoFileClip: The loaded video clip.

        Raises:
            ValueError: If the specified file field is invalid or not a video file.
        """
        text_file_instance= self.text_file_instance
        try:
            # Check if the specified file field exists and is valid
            if not hasattr(text_file_instance, file_field):
                raise ValueError(f"{file_field} does not exist in text_file_instance.")

            video_file_field = getattr(text_file_instance, file_field)

            if not video_file_field or not video_file_field.name:
                raise ValueError(
                    f"Video S3 key is empty for {file_field} in the text_file_instance."
                )

            file_extension = os.path.splitext(video_file_field.name)[1].lower()

            with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_video:
                video_content = download_from_s3(video_file_field.name, temp_video.name)

                if not video_content:
                    raise ValueError("Failed to download the video from S3.")

                with open(temp_video.name, "wb") as video_file:
                    video_file.write(video_content)

            # Check if the downloaded file is a valid video
            video_clip = VideoFileClip(os.path.normpath(temp_video.name))

            # Check for duration or any other validation if needed
            if video_clip.duration <= 0:
                raise ValueError("Downloaded file is not a valid video.")

            # Return the video clip
            return video_clip

        except Exception as e:
            logging.error(f"Error loading video from text_file_instance: {e}")
            raise
    def trim_video_(self):
        clip= self.load_video_from_instance('video_file')
        self.text_file_instance.track_progress(25)
        clip=clip.subclip(self.text_file_instance.timestamp_start,self.text_file_instance.timestamp_end)
        self.text_file_instance.track_progress(35)


        
        with tempfile.NamedTemporaryFile(
            suffix=".mp4", delete=False
            ) as temp_output_video:

            self.text_file_instance.track_progress(40)

            clip.write_videofile(
                temp_output_video.name,
                codec="libx264",
                preset="ultrafast",
                fps=30,
                audio_codec="aac",
                ffmpeg_params=["-movflags", "+faststart"],
            )

            # Save the watermarked video to the generated_watermarked_video field
            if self.text_file_instance.trimmed_video:
                self.text_file_instance.trimmed_video.delete(save=False)

            self.text_file_instance.trimmed_video.save(
                f"final_{self.text_file_instance.id}_.mp4",
                ContentFile(open(temp_output_video.name, "rb").read()),
            )
            self.text_file_instance.track_progress(100)
            return True



