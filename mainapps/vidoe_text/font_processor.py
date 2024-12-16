import os
import shutil
from xml.etree import ElementTree as ET
from django.conf import settings

# Paths
FONTS_DIR = os.path.join(settings.BASE_DIR, 'fonts')  
CONTAINER_FONTS_DIR = "/usr/share/fonts/fonts"  
TYPE_GHOSTSCRIPT_XML = "/etc/ImageMagick-6/type-ghostscript.xml"

SUPPORTED_FORMATS = ["ttf", "otf", "woff", "woff2"] 


def handle_font_upload(font_file):
    """
    Handles uploading and registering font files.
    """
    font_name, font_extension = os.path.splitext(font_file.name)
    font_extension = font_extension.lower().strip(".") 

    if font_extension not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported font format: {font_extension}")

    os.makedirs(FONTS_DIR, exist_ok=True)
    local_font_path = os.path.join(FONTS_DIR, font_file.name)

    if not os.path.exists(local_font_path):
        with open(local_font_path, "wb") as f:
            for chunk in font_file.chunks():
                f.write(chunk)
        print(f"Font saved: {local_font_path}")

    shutil.copytree(FONTS_DIR, CONTAINER_FONTS_DIR, dirs_exist_ok=True)
    print(f"Fonts copied to Docker container: {CONTAINER_FONTS_DIR}")

    add_font_to_ghostscript(font_name, font_extension, local_font_path)


def add_font_to_ghostscript(font_name, font_format, font_path):
    """
    Adds a font to ImageMagick's type-ghostscript.xml file if not already present.
    """
    # Parse the XML
    tree = ET.parse(TYPE_GHOSTSCRIPT_XML)
    root = tree.getroot()

    # Check if the font is already listed
    for element in root.findall("type"):
        if element.attrib.get("name") == font_name and element.attrib.get("glyphs") == font_path:
            print(f"Font '{font_name}' is already in type-ghostscript.xml")
            return

    # Add the new font entry
    new_font = ET.Element(
        "type",
        attrib={
            "name": font_name,
            "format": font_format,
            "glyphs": font_path,
        },
    )
    root.append(new_font)

    # Write changes back to the XML file
    tree.write(TYPE_GHOSTSCRIPT_XML)
    print(f"Font '{font_name}' added to type-ghostscript.xml")
