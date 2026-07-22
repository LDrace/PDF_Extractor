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