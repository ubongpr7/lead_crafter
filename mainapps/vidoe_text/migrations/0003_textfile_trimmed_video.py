# Generated by Django 4.2.16 on 2024-12-11 14:38

from django.db import migrations, models
import mainapps.vidoe_text.models


class Migration(migrations.Migration):

    dependencies = [
        ('vidoe_text', '0002_remove_textfile_fps_textfile_resolution_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='textfile',
            name='trimmed_video',
            field=models.FileField(blank=True, null=True, upload_to=mainapps.vidoe_text.models.video_file_upload_path),
        ),
    ]