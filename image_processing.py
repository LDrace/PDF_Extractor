import io
import pymupdf as pdf
from PIL import Image

def has_transparency(img):
    """
    This is used to determine if images have transparency. 
    Should return True if they do and False if they don't. 
    Detects RGBA, LA (Greyscale + Alpha), and palettized (P) modes.
    Currently only called once in sort-files-automatically.py
    """

    if img.mode in ("RGBA", "LA"):
        alpha_min, _ = img.getchannel('A').getextrema()
        return alpha_min < 255
    return img.mode == "P" and "transparency" in img.info

def get_uniformity(img, ignore_transparency:bool = False, fast:bool = True):
    """
    Function to evaluate image uniformity and return a float between 0 and 100, where 0 means every pixel is different, and 100 is every pixel shares the same color. 50 would mean half the pixels in the image share the same color
    I decided to let it ignore alpha/transparency. Second argument is ignore_transparency which is a boolean. True only counts pixels that are not fully transparent, False does not. In the case that ALL pixels are transparent, returns 100.
    The fast argument speeds up the function by shrinking the image to a thumbnail at 100x100px, then evaluating it. This saves a lot of time, but it can be turned off to evaluate at the full resolution by making fast = False.
    """
    # make a small copy for evaluation if fast = True
    if fast:
        temp_img = img.copy()
        temp_img.thumbnail((100, 100))
    else:
        temp_img = img
    
    # check if ignore_transparency = True and if the image has an alpha channel
    if ignore_transparency and "A" in temp_img.getbands():
        # put the image in the right mode so we can actually see the alpha, 
        if temp_img.mode not in ("RGBA", "LA"):
            temp_img = temp_img.convert("RGBA")

    # now count the number of pixels and the number of colors
    total_pixels = temp_img.width * temp_img.height
    colors = temp_img.getcolors(maxcolors=total_pixels) or []

    # if getcolors() crashes here, the function returns 0.0. pdf extraction can return unusually large or corrupted files, so this is a hedge against that possibility
    if not colors:
        return 0.0

    if ignore_transparency and "A" in temp_img.getbands():
        # this replaces colors and total_pixels in normal behavior
        visible_colors = []
        visible_pixels = 0

        # count every pixel and ignore transparent ones
        for count, color in colors:
            if color[-1] > 0:
                visible_colors.append((count,color))
                visible_pixels += count

        # edge case for fully transparent images. the compression from fast=True could theoretically remove visible pixels, so we evaluate again just to be sure we aren't throwing away a little icon or something
        if visible_pixels == 0:
            if fast:
                return get_uniformity(img, ignore_transparency=True, fast=False)
            return 100.0
    
        most_common_count = max(count for count, color in visible_colors)
        return (most_common_count / visible_pixels) * 100

    # standard behavior for opaque images or when ignore_transparency = False
    else:
        most_common_count = max(count for count, color in colors)
        return (most_common_count / total_pixels) * 100

def check_xref_duplicates(metadata_stream):
    """
    Checks a metadata dictionary and yields it back only if this is a unique image that has not been seen yet.
    """
    seen = set()

    for meta in metadata_stream:
        xref = meta['xref']

        if xref not in seen:
            seen.add(xref)
            yield meta

def meta_analysis(metadata_stream: dict, log = 0, junk_size = 200, symbol_size = 500, junk_ratio = 3):
    """
    Adds categories to the end of metadata from get_image_metadata based on their metadata, and yields the updated metadata.
    """
    for meta in metadata_stream:
        if log >= 1:
            print(f"Performing meta analysis for an image on {meta['page_number']} with xref {meta['xref']}...")

        # here we add a bunch of new trackers to the metadata dictionary for sorting
        # scores are for evaluating the images
        # score_reasons and tag_reasons are for debugging
        meta['junk score'] = 0
        meta['symbol score'] = 0
        meta['art score'] = 0
        meta['character score'] = 0
        meta['score_reasons'] = []

        # tags are for special cases, like an image requiring a special process or needing to be saved as a particular filetype
        meta['tags'] = []
        meta['tag_reasons'] = []
        
        # check width and height
        width = meta['width']
        height = meta['height']

        # combine width and height into a tuple for size
        size = (width, height)

        # check the compression filter, bits per component, and colorspace, and check for an smask
        img_filter = str(meta.get('filter', '')) # blank fallback if the filter is missing, this must be a string
        colorspace = str(meta.get('colorspace', '')) # fallback to an empty string if colorspace is missing, this must be a string
        smask = meta.get('smask', 0) # fallback to 0 if smask is missing
        bpc = meta.get('bpc', 0) # fallback to 0 if the bits per component is missing

        # checks for dimensions
        if min(size) <= junk_size:
            meta['junk score'] += 2
            meta['score_reasons'].append("below minimum size")

        if max(size) >= junk_ratio * min(size):
            meta['junk score'] += 2
            meta['score_reasons'].append("extreme dimensions")

        elif min(size) <= symbol_size:
            meta['symbol score'] += 2
            meta['score_reasons'].append("within symbol size range")

        # certain filters are only used for certain kinds of images. DCTDecode is usually used for JPEGs
        # check for an smask here because if the compressed image is made transparent inside the PDF with a mask, it can still be extracted with transparency
        if 'DCTDecode' in img_filter and smask == 0:
            meta['art score'] += 2
            meta['score_reasons'].append("opaque image")
            meta['tags'].append("jpg")
            meta['tag_reasons'].append("opaque image with DCTDecode")
            
            if log >= 1:
                print(f"Image was assigned the following tag(s): {meta['tags']} ({meta['tag_reasons']}).")

        # CCITTFaxDecode is for momochrome images, and 1-bit images can only be monochrome. These are probably never worth keeping
        elif 'CCITTFaxDecode' in img_filter or bpc == 1:
            meta['junk score'] += 3
            meta['score_reasons'].append("1 bpc or CCITTFaxDecode: monochrome image")

        # Indexed colorspaces use a palette. This is most likely a flat vector image or line art, a.k.a. junk.
        elif 'Indexed' in colorspace:
            meta['junk score'] += 1
            meta['score_reasons'].append("Indexed colorspace")

        # Cyan Magenta Yellow and Key is for subtractive color printing. These are likely artworks.
        elif 'DeviceCMYK' in colorspace:
            meta['art score'] += 2
            meta['score_reasons'].append("CMYK colorspace")

        # if this image has an smask and it is not rendered with an opaque colorspace, it may have transparency
        if smask > 0:

            meta['character score'] += 3
            meta['symbol score'] += 2
            meta['art score'] += 1
            meta['score_reasons'].append("has transparency")

            meta['tags'].extend(["reconstruct", "png"])
            meta['tag_reasons'].append("has smask")

            if log >= 1:
                print(f"Image was assigned the following tag(s): {meta['tags']} ({meta['tag_reasons']}).")
        
        if log >= 1:
            print(f"Analysis complete: Junk score: {meta['junk score']}, Symbol score: {meta['symbol score']}, Art score: {meta['art score']}, Character score: {meta['character score']}, \nReasons: {meta['score_reasons']}.")

        yield meta

def route(metadata_stream:dict, log:int = 0, reconstruct:bool=True, decompress:bool=False):
    """
    Decides which process to send files to based on their assigned categories.
    """
    for meta in metadata_stream:
        if log >= 1:
            print(f"Determining next step for an image on {meta['page']} with xref {meta['xref']}...")

        # first, check that a category has been assigned. If the image has not been categorized yet, send it to meta analysis
        if 'category' not in meta:
            if log >= 1:
                print("Sending image to meta analysis.")
            yield meta_analysis(metadata_stream=meta)

        # if there is a category, we'll need to know what it is
        category = meta['category']
        category_reason = meta['category_reason']

        # if the image is junk, this is the end of the line. Add the xref of the image to a list so this image is not checked again.
        if category == 'junk':
            if log >= 1:
                print("Skipping junk image.")  

        if category == 'reconstruct':
            if log >= 1:
                print("Found image with transparency mask. Preparing image for reconstruction.")


def reconstruct(pdf_path: str, metadata_stream):
    """
    Attempt reconstruction for an image with a mask.
    """
    for meta in metadata_stream:
        xref = meta['xref']
        smask = meta.get('smask', 0)