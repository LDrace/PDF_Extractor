import utils
import io
import os
import pymupdf as pdf
import extractor as ex

from PIL import Image

pdfname = ('test.pdf')
meta_stream = ex.get_image_metadata(pdfname)
output_path = "./output"
saved_images = 0

for meta, pil_img in ex.extract_pillow_images(pdfname, meta_stream):
    saved_images += 1
    imagename = f"img{saved_images}.png"
    path = os.path.join(output_path, imagename)
    print(path)
    pil_img.save(path)