import io
import pymupdf as pdf
from PIL import Image

def meta_analysis(metadata_stream: dict, log = 0, min_size = 100, junk_ratio = 3):
    """
    Adds categories to the end of metadata from get_image_metadata based on their metadata, and yields the updated metadata.
    """
    for meta in metadata_stream:
        if log >= 1:
            print(f"Performing metanalysis for an image on {meta['page']} with xref {meta['xref']}...")
        
        # check width and height
        width = meta['width']
        height = meta['height']
        size = (width, height)

        # check if there could be transparency stored in an smask
        smask = meta.get('smask', 0) # fallback to 0 if smask is missing

        # exclude very tiny images
        if min(size) <= min_size:
            meta['category'] = "junk"
            meta['category_reason'] = "below minimum size"

        # exclude images with extreme dimensions
        elif max(size) >= junk_ratio * min(size):
            meta['category'] = "junk"
            meta['category_reason'] = "extreme dimensions"

        # mark the image as requiring reconstruction
        elif smask > 0:
            
            meta['category'] = "reconstruct"
            meta['category_reason'] = "has smask"

        # unsorted images will need to be analized on more than their metadata
        else:
            meta['category'] = "unsorted"
            meta['category_reason'] = "last finished meta analysis"
        
        if log >= 1:
            print(f"Analysis complete: {meta['category']} ({meta['category_reason']})")

        yield meta

def reconstructpix(pdf_path: str, metadata_stream):
    """
    Attempt reconstruction for an image with a mask.
    """
    for meta in metadata_stream:
        xref = meta['xref']
        smask = meta.get('smask', 0)
