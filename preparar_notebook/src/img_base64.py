import base64
from PIL import Image
from io import BytesIO

def base64_to_base64raw(img_base64):
    start_position = 0
    for i in range(len(img_base64)):
        if img_base64[i:].startswith('base64'):
            start_position = i + 7
            break
    return img_base64[start_position:]

def base64_to_webp(img_base64, output_file, quality=75):
    img_base64 = base64_to_base64raw(img_base64)        # Remove 'data:image/png;base64,' from base64
    image_data = base64.b64decode(img_base64)           # Decode base64
    image = Image.open(BytesIO(image_data))             # Convert data image to PIL Image
    image.save(output_file, 'WEBP', quality=quality)    # Save image in WEBP format

def base64_to_png(img_base64, output_file):
    img_base64 = base64_to_base64raw(img_base64)        # Remove 'data:image/png;base64,' from base64
    image_data = base64.b64decode(img_base64)           # Decode base64
    with open('output_image.png', 'wb') as image_file:  # Open file in binary write mode
        image_file.write(image_data)                    # Save image in PNG format