import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from mainapps.audio.models import BackgroundMusic
from mainapps.vidoe_text.decorators import (
    check_credits_and_ownership,
    check_user_credits,
)
from mainapps.vidoe_text.font_processor import handle_font_upload
from .models import TextFile, TextLineVideoClip
import os
from django.http import HttpResponse, JsonResponse, Http404
from django.conf import settings
from django.urls import reverse
import logging
import requests
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.core.files.base import ContentFile
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.apps import apps
import tempfile


@require_http_methods(["DELETE"])
def delete_background_music(request, id):
    try:
        # Get the BackgroundMusic object with the given id
        background_music = get_object_or_404(BackgroundMusic, id=id)

        # Delete the object
        background_music.music.delete()
        background_music.delete()

        # Return a success response
        return JsonResponse({"message": "Music deleted successfully!"}, status=200)
    except Exception as e:
        # Return an error response in case something goes wrong
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["DELETE"])
def delete_clip(request, id):
    try:
        clip = get_object_or_404(TextLineVideoClip, id=id)

        clip.video_file_path.delete()
        clip.delete()

        return JsonResponse({"message": "Music deleted successfully!"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def check_credits(api_key):
    # Define the endpoint for fetching user information
    url = "https://api.elevenlabs.io/v1/usage/character-stats"

    # Set the headers with the API key for authentication
    headers = {
        "xi-api-key": api_key,
    }

    # Make the request to the ElevenLabs API
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        remaining_credits = response.json()

        # Extract the subscription information

        print(f"Remaining Credits: {remaining_credits}")
        return f"Remaining Credits: {remaining_credits}"
    else:
        print(f"Failed to fetch user info. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def is_api_key_valid(api_key, voice_id):
    """
    Checks if the given ElevenLabs API key is valid.

    Args:
        api_key (str): The ElevenLabs API key to check.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    endpoint_url = f"https://api.elevenlabs.io/v1/voices"
    endpoint_url_2 = f"https://api.elevenlabs.io/v1/voices/{voice_id}"

    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    x, y = False, False
    try:
        response = requests.get(endpoint_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        # Check p response content or status code to determine validity
        if response.status_code == 200:
            x = True

    except requests.RequestException as e:
        print(f"Error checking API key: {e}")
    try:
        response_2 = requests.get(endpoint_url_2, headers=headers)
        if response_2.status_code == 200:
            y = True

    except requests.RequestException as e:
        print(f"Error checking API key: {e}")

    return x, y


def convert_to_seconds(time_str):
    try:
        minutes, seconds = map(float, time_str.split(":"))
        return minutes * 60 + seconds
    except ValueError:
        return 0.0  # Return 0 or handle error as needed


def format_seconds_to_mm_ss(seconds):
    """Convert seconds to mm:ss format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02}:{secs:02}"


def serve_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    with open(file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


@login_required
@check_credits_and_ownership(textfile_id_param="textfile_id", credits_required=1)
def process_background_music(request, textfile_id):
    # Run process_video command in a new thread
    def run_process_command(textfile_id):
        try:
            call_command("music_processor", textfile_id)
        except Exception as e:
            # Handle the exception as needed (e.g., log it)
            print(f"Error processing video: {e}")

    textfile = TextFile.objects.get(pk=textfile_id)
    textfile.progress = "0"
    textfile.save()
    musics = textfile.background_musics.all()
    n_musics = len(musics)

    if request.method == "POST" :
        if not textfile.text_file:
            return JsonResponse({"error": "Text file is missing."}, status=400)
        
        no_of_mp3 = int(request.POST.get("no_of_mp3", 0))  # Number of MP3 files
        for music in textfile.background_musics.all():
            music_file=request.POST.get(f'saved-mp3-{music.id}')
            start=request.POST.get(f'saved-starts-{music.id}')
            end=request.POST.get(f'saved-ends-{music.id}')
            volume=request.POST.get(f'saved-volume-{music.id}')
            if music_file:
                music.music.delete(save=False)
                music.music=music_file
            if start:
                music.start_time=convert_to_seconds(start)
            if end:
                music.end_time=convert_to_seconds(end)
            if volume:
                music.bg_level=float(volume)/1000.0
            music.save()



        music_files = []
        music_files_dict = {}
        start_times_str = {}
        bg_levels = {}
        end_times_str = {}

        for i in range(1, no_of_mp3 + 1):
            music_file = request.FILES.get(f"mp3-{i}")
            if music_file is not None:
                music_files.append(music_file)
                music_files_dict[f"bg_music_{i}"] = music_file

            start_time = request.POST.get(f"starts-{i}")
            if start_time is not None:
                start_times_str[f"bg_music_{i}"] = start_time

            bg_level = request.POST.get(f"volume-{i}")
            if bg_level is not None:
                bg_levels[f"bg_music_{i}"] = float(bg_level) / 1000.0

            end_time = request.POST.get(f"ends-{i}")
            if end_time is not None:
                end_times_str[f"bg_music_{i}"] = end_time

        start_times = [
            convert_to_seconds(time_str) for time_str in start_times_str.values()
        ]
        end_times = [
            convert_to_seconds(time_str) for time_str in end_times_str.values()
        ]

        bg_musics = []
        for i in range(1, no_of_mp3 + 1):
            if music_files_dict.get(f"bg_music_{i}"):
                bg_music = BackgroundMusic(
                    text_file=textfile,
                    music=music_files_dict[f"bg_music_{i}"],
                    start_time=convert_to_seconds(start_times_str[f"bg_music_{i}"]),
                    end_time=convert_to_seconds(end_times_str[f"bg_music_{i}"]),
                    bg_level=bg_levels[f"bg_music_{i}"],
                )

                bg_musics.append(bg_music)
        if bg_musics:
            BackgroundMusic.objects.bulk_create(bg_musics)
        
        lines = []
        bg_musics_updated=textfile.background_musics.all()

        for bg_music in bg_musics_updated:
            start_time_str = bg_music.start_time
            end_time_str = bg_music.end_time
            bg_level = str(float(bg_music.bg_level))
            lines.append(
                f"{bg_music.music.name} {start_time_str} {end_time_str} {bg_level}"
            )

        content = "\n".join(lines)

        file_name = f"background_music_info_{textfile_id}_.txt"

        textfile.bg_music_text.save(file_name, ContentFile(content))
        textfile.save()

        try:
            thread = threading.Thread(target=run_process_command, args=(textfile_id,))
            thread.start()
            return redirect(f"/text/progress_page/bg_music/{textfile_id}")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    

    return render(
        request,
        "lead-maker/music.html",
        {
            "textfile_id": textfile_id,
            "textfile": textfile,
            "musics": musics,
            "n_musics": n_musics,
        },
    )


def clean_progress_file(text_file_id):
    """Deletes the progress file after 3 seconds when progress is 100%."""
    if os.path.exists(f"{settings.MEDIA_ROOT}/{text_file_id}_progress.txt"):
        os.remove(f"{settings.MEDIA_ROOT}/{text_file_id}_progress.txt")


def progress(request, text_file_id):
    text_file = TextFile.objects.get(id=text_file_id)
    try:
        return JsonResponse({"progress": int(text_file.progress)})
    except:
        messages.error(request, f"{text_file.progress}")
        return JsonResponse({"error": text_file.progress})


@login_required
def progress_page(request, al_the_way, text_file_id):
    return render(
        request,
        "lead-maker/loading.html",
        {"al_the_way": al_the_way, "text_file_id": text_file_id},
    )



def validate_api_key(api_key, voice_id):
    # Try making a request to Eleven Labs API to validate the key
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key}
    data = {
        "text": "Test voice synthesis",  # Small test text to avoid large requests
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return {"valid": True}
        elif response.status_code == 401:
            error_detail = response.json().get("detail", {})
            if "status" in error_detail and error_detail["status"] == "quota_exceeded":
                return {
                    "valid": False,
                    "error": f"Quota exceeded: {error_detail.get('message', 'Insufficient credits')}",
                }
            else:
                return {"valid": False, "error": "Invalid API key"}
        else:
            return {"valid": False, "error": f"Invalid Voice ID"}
    except requests.exceptions.RequestException as e:
        return {"valid": False, "error": "Error connecting to Eleven Labs API"}


def validate_api_keyv(request):
    if request.method == "POST":
        api_key = request.POST.get("eleven_labs_api_key", "")
        voice_id = request.POST.get("voice_id")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key}
        data = {
            "text": "Test voice synthesis",
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                return JsonResponse({"valid": True})
            elif response.status_code == 401:
                error_detail = response.json().get("detail", {})
                if (
                    "status" in error_detail
                    and error_detail["status"] == "quota_exceeded"
                ):
                    return JsonResponse(
                        {
                            "valid": False,
                            "error": f"Quota exceeded: {error_detail.get('message', 'Insufficient credits')}",
                        }
                    )
                else:
                    return JsonResponse({"valid": False, "error": "Invalid API key"})
            else:
                return JsonResponse({"valid": False, "error": "Invalid Voice ID"})
        except requests.exceptions.RequestException:
            return JsonResponse(
                {"valid": False, "error": "Error connecting to Eleven Labs API"}
            )

    return JsonResponse({"valid": False, "error": "Invalid request method"})


@login_required
@check_user_credits(minimum_credits_required=1)
def add_text_video(request):
    if request.method == "POST":
        videoFile = request.FILES.get("videoFile")
        voice_id = request.POST.get("voiceid")
        api_key = request.POST.get("elevenlabs_apikey")
        resolution = request.POST.get("resolution")
        fontFile = request.FILES.get("fontFile")
        font_color = request.POST.get("font_color")
        subtitle_box_color = request.POST.get("subtitle_box_color")
        font_select = request.POST.get("font_select")
        font_size = request.POST.get("font_size")
        print('======>',font_size)

        x, y = is_api_key_valid(api_key, voice_id)
        try:
            # Process the uploaded font
            handle_font_upload(fontFile)
            
        except Exception as _:
            print(_)
        if x and y:
            if voice_id and api_key:
                text_obj = TextFile.objects.create(
                    user=request.user,
                    video_file=videoFile,
                    voice_id=voice_id,
                    api_key=api_key,
                    font_file=fontFile,
                    font = os.path.splitext(fontFile.name)[0],
                    resolution=resolution,
                    subtitle_box_color=subtitle_box_color,
                    font_size=font_size,
                    font_color=font_color,
                )

                return redirect(f'/text/trim-video/{text_obj.id}')

            else:
                messages.error(request, "Please provide all required fields.")
                
                return render(
                    request,
                    "lead-maker/add_text_video.html",
                    {"error": "Please provide all required fields."},
                )
        elif x and not y:
            messages.error(
                request,
                "The voice ID you provided is invalid, please provide a valid one",
            )
            return render(
                request,
                "lead-maker/add_text_video.html",
                {"error": "Please provide valid API key"},
            )
        elif not x:
            messages.error(
                request,
                "The API key you provided is invalid, please provide a valid one!",
            )
            return render(
                request,
                "lead-maker/add_text_video.html",
                {"error": "Please provide valid API key"},
            )

    return render(request, "lead-maker/add_text_video.html",)


@login_required
@check_credits_and_ownership(textfile_id_param="textfile_id", credits_required=1)
def download_video(
    request,
    textfile_id,
):
    text_file = TextFile.objects.get(pk=textfile_id)
    if request.user.subscription.credits > 0:
        bg_music = request.GET.get("bg_music", None)

        return render(
            request,
            "lead-maker/Download.html",
            {
                "textfile_id": textfile_id,
                "bg_music": bg_music,
                "text_file": text_file,
                "plans": apps.get_model("accounts", "Plan").objects.all(),
            },
        )
    else:
        messages.info(request, "You do not have enough credit to Proceed")
        return redirect(reverse("home:home") + "#pricing")

@login_required
@check_credits_and_ownership(textfile_id_param="textfile_id", credits_required=1)
def trim_video(request,textfile_id):

    text_file=TextFile.objects.get(id=textfile_id)
    def run_trim_command(textfile_id):
        try:
            call_command("trim_video", textfile_id)
        except Exception as e:
            print(f"Error processing video: {e}")

    if request.method=="POST":
        start=float(request.POST.get('start'))
        end=float(request.POST.get('end'))
        text_file.timestamp_start=start
        text_file.timestamp_end=end
        text_file.save()
        thread = threading.Thread(target=run_trim_command, args=(textfile_id,))
        thread.start()

    
        return redirect(f'/text/progress_page/trim/{text_file.id}')
    else:
        if text_file.trimmed_video:
            text_file.trimmed_video.delete(save=True)
            text_file.save()
    return render(request,'lead-maker/trim_video.html',{'text_file':text_file})

@login_required
@check_credits_and_ownership(textfile_id_param="textfile_id", credits_required=1)
def add_leads(request,textfile_id):
    text_file=TextFile.objects.get(id=textfile_id)
    line_clips= TextLineVideoClip.objects.filter(text_file=text_file)
    no_of_slides= len(line_clips)
    if line_clips:
        clip_line_nums=[clip.line_number for clip in line_clips ]
        max_lin_num=max(clip_line_nums)
    else: 
        max_lin_num=0
    context={
        'text_file':text_file,
        'clips':line_clips,
        "no_of_slides":no_of_slides
        }
    def run_add_lead_command(textfile_id):
        try:
            call_command("add_leads", textfile_id)
        except Exception as e:
            print(f"Error processing video: {e}")

    if request.method=="POST":
        text_file.progress='0'
        text_file.save()
        n_slides= int(request.POST.get('no_of_slides'))
        for clip in line_clips:
            clip_text= request.POST.get(f'saved_slide_text_{clip.id}')
            clip_file= request.FILES.get(f'saved_slide_file_{clip.id}')
            if clip_text:
                clip.text=""
                clip.text=clip_text
            if clip_file:
                clip.video_file_path.delete(save=False)
                clip.video_file_path=clip_file
            clip.save()
        
        slides=[]
        for n in range(1,n_slides+1):
            print("this is is slide: ",n)
            slide_text=request.POST.get(f'slide_text_{n}')
            video_file_path= request.FILES.get(f'slide_file_{n}')
            if video_file_path:
                    
                clip=TextLineVideoClip(
                    text_file=text_file,
                    video_file_path=video_file_path,
                    text=slide_text ,
                    line_number=n+max_lin_num,
                )
                slides.append(clip)
                print("appended clip for: ",n)

        clips=TextLineVideoClip.objects.bulk_create(slides)
        save_clips_to_text_file(text_file)
        thread = threading.Thread(target=run_add_lead_command, args=(textfile_id,))
        thread.start()

        return redirect(f'/text/progress_page/add_leads/{textfile_id}') 
        


    return render(request, 'lead-maker/add-leads.html',context)

def save_clips_to_text_file(text_file):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        for clip in text_file.video_clips.all():
            if clip.text: 
                temp_file.write(clip.text + '\n')
        
        temp_file.flush()
        temp_file.seek(0)

        with open(temp_file.name, 'rb') as f:
            if text_file.text_file:
                text_file.text_file.delete(save=False)
            text_file.text_file.save(f'clips_text_{text_file.id}.txt', f)

    

@login_required
def download_file_from_s3(request, file_key, textfile_id=None):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    if textfile_id:
        text_file = TextFile.objects.get(id=textfile_id)
        user_sub = request.user.subscription
        if user_sub.credits > 0:
            if not text_file.processed:
                user_sub.credits -= 1
                user_sub.save()

                text_file.processed = True
                text_file.save()

            try:
                # Get the file from S3
                s3_response = s3.get_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key
                )
                print('===========>',file_key)

                # Set the appropriate headers for file download
                response = HttpResponse(
                    s3_response["Body"].read(), content_type=s3_response["ContentType"]
                )
                
                if file_key == "logos/VSL-Maker-Script-Template.txt":
                    custom_filename = "VideoCrafter.txt"
                    response["Content-Disposition"] = f'attachment; filename="{custom_filename}"'
                else:
                    response["Content-Disposition"] = (
                        f'attachment; filename="{file_key.split("/")[-1]}"'
                    )
                
                response["Content-Length"] = s3_response["ContentLength"]

                return response
            except s3.exceptions.NoSuchKey:
                return HttpResponse("File not found.", status=404)
            except (NoCredentialsError, PartialCredentialsError):
                return HttpResponse("Credentials not available.", status=403)
        return HttpResponse(status=403)

    else:
        try:
            # Get the file from S3
            s3_response = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key
            )
            print('===========>',file_key)
            # Set the appropriate headers for file download
            response = HttpResponse(
                s3_response["Body"].read(), content_type=s3_response["ContentType"]
            )
            if file_key == "logos/VSL-Maker-Script-Template.txt":
                custom_filename = "VideoCrafter.txt"
                response["Content-Disposition"] = f'attachment; filename="{custom_filename}"'
            else:
                response["Content-Disposition"] = (
                    f'attachment; filename="{file_key.split("/")[-1]}"'
                )
            response["Content-Length"] = s3_response["ContentLength"]

            return response
        except s3.exceptions.NoSuchKey:
            return HttpResponse("File not found.", status=404)
        except (NoCredentialsError, PartialCredentialsError):
            return HttpResponse("Credentials not available.", status=403)

    return HttpResponse(status=403)