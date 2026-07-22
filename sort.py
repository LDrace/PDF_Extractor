import os
import utils
from PIL import Image

def sort_automatic(
    extract_output = "./output", 
    sort_output = "./sorted images", 
    symbol_size = 500,
    symbol_ratio = 1.5,
    junk_ratio = 2.8,
    junk_max_uniformity = 60):
    """
    Opens images in the extract_output path and sorts them into subfolders in the the sort_output path. 
    Other arguments determine how images are sorted.
    symbol_size: The maximum either dimension can be before an image can no longer be considered a "symbol"
    symbol_ratio: Ensures that symbols are more square. 1 = perfectly square, higher values = less square.
    junk_ratio: Ensures that junk is less square. Reverse of symbol_ratio. 
    junk_max_uniformity: Images above this level of uniformity are junk. 80 = 80% one color. 
    """
    
    # for gui and exception handling
    task = "sorting images"

    # subfolders for sorting
    subfolders = {
        "creatures":"./sorted images/creatures", 
        "symbols":"./sorted images/symbols",
        "art":"./sorted images/art",
        "junk":"./sorted images/junk"}

    # makes the output folders if they don't exist
    os.makedirs(sort_output, exist_ok=True)
    for subfolder in subfolders.values(): 
        os.makedirs(sort_output, exist_ok=True)

    # image filepaths will be sorted into this dictionary
    sorted_images = {"creatures": [], "symbols": [], "art": [], "junk": []} 

    # initialize variables for print output at the end
    num_unsorted = 0

    # get filepaths for each image
    for file in os.listdir(extract_output): 
        file_path = os.path.join(extract_output, file)
        
        if os.path.isdir(file_path):
            continue

    # sorting is done here, wrapped in try in case the file can't be opened
        try:
            with Image.open(file_path) as img:
                if utils.get_uniformity(img, ignore_transparency = True, fast= True) > junk_max_uniformity:
                    category = "junk"
                elif max(img.size) >= junk_ratio * min(img.size):
                    category = "junk"
                elif any(n <= symbol_size for n in img.size) and max(img.size) <= symbol_ratio * min(img.size):
                    category = "symbols"
                elif img.format == "JPEG" or img.mode == "CMYK":
                    category = "art"    
                elif utils.has_transparency(img):
                    category = "creatures"
                elif any(n >= symbol_size for n in img.size):
                    category = "art"
                else:
                    category = "junk"

    # when the file is closed, check to be sure there was a category assigned, then move the file accordingly
            if category:
                sorted_images[category].append(file)
                destination = os.path.join(subfolders[category], file)
                utils.move_handler(file_path, destination, task=task)

    # files that cannot be identified as images are skipped
        except Image.UnidentifiedImageError:
            num_unsorted += 1

    # now tell the user what happened
    num_sorted = sum(len(images) for images in sorted_images.values())

    if num_sorted == 0 and num_unsorted == 0:
        print("No images found.")
    else:
        if num_unsorted > 0:
            print(f"{num_sorted} images were successfully sorted.\n{num_unsorted} files could not be sorted.")
        
        else:
            print(f"All {num_sorted} images were successfully sorted!")
        
        print("Images were sorted as follows:")
        print(f"{len(sorted_images['creatures'])} creatures, {len(sorted_images['symbols'])} symbols, {len(sorted_images['art'])} art, and {len(sorted_images['junk'])} junk.")

if __name__ == "__main__":
    sort_automatic()