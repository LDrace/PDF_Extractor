import os
import utils

from PIL import Image

evaluate = "D:\Projects\Python\PDF Extractor\sorted images\creatures"

failed_eval = 0

for file in os.listdir(evaluate): 
    file_path = os.path.join(evaluate, file)
    
    if os.path.isdir(file_path): 
        continue

    try:
        with Image.open(file_path) as img:
            print(f"{file_path} uniformity: {utils.get_uniformity(img, ignore_transparency=True, fast=True)}")

    except Image.UnidentifiedImageError:
        failed_eval += 1

print(f"Failed evaulations: {failed_eval}")