import utils
import io
import pymupdf as pdf

from PIL import Image

def ordinal(n):
    """
    Takes a number and returns a string with its ordinal. Converts negatives to absolute values. Used for logging readability.
    """
    # Convert our number into an absolute number
    f = abs(n)
    # Check for 11, 12, 13 which are exceptions to the normal rule
    if 11 <= f % 100 <= 13:
        suffix = "th"
    else:
        # Match the last digit to the correct suffix
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(f % 10, "th")
    # Return the number with its ordinal
    return f"{n}{suffix}"

DEFAULT_KEYS = ['xref', 'smask', 'width', 'height', 'bpc', 'colorspace', 'altcolorspace', 'name', 'filter', 'referencer']

def get_image_metadata(pdf_path: str, pages: tuple[int, int] = None, keys: list[str] = None, log = 0):
    """
    Looks for images in a PDF in a given range of pages and yields a dictionary containing their metadata.
    Note: this function contains the ordinal() function, defined above.
    
    Arguments:
        pdf_path: the path to the PDF
        pages: this tuple defines the range of pages to search, starting with the first page number and ending with the last (inclusive). If pages = None, scans the entire document. 
        keys defines the names for the keys in the dictionary. Defaults defined above, outside the function in DEFAULT_KEYS
        log: prints to the CIL if the keys are modified and prints how many images are found on each page if log >= 1. Additionally prints readable image dictionaries if log >= 2.
    """
    # consult the keys argument to see if we need to change the key names
    if keys is None:
        img_keys = DEFAULT_KEYS
    else:
        img_keys = keys
        if log >= 1:
            print(f"Keys modified with the following argument:{img_keys}")

    # open the doc
    with pdf.open(pdf_path) as doc:

        # consult the pages argument for which pages to check
        if pages is None:
            page_range = range(len(doc))
        else:
            page_range = range(pages[0], pages[1] + 1)

        # check pages for images
        for page in page_range:
            images = doc.get_page_images(page, full=True)
            if log >= 1:
                print(f"Found {len(images)} image(s) on page {page + 1}.")

            # make a dictionary out of the image using the keys from the argument above
            for img_index, img_tuple in enumerate(images):
                meta = dict(zip(img_keys, img_tuple, strict=True))
                meta['page_number'] = page + 1
                if log >= 2:
                    print(f"{ordinal(img_index + 1)} image metadata from page {page + 1}:")
                    for key, value in meta.items():
                        print(f" {key}: {value}")

                # pass the dictionary
                yield meta

for item in get_image_metadata("test.pdf", log=2):
    print(item)