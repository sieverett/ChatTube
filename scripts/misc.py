from PIL import Image

def reduce_image_size(image_path, output_path, size):
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(output_path, "PNG")