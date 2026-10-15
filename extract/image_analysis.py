import os
from PIL import Image

extraction_output = "./output"

# Dictionary for mode counts
mode_counts = {}
num_unidentified = 0

for file in os.listdir(extraction_output): 
    file_path = os.path.join(extraction_output, file)
    
    if os.path.isdir(file_path): 
        continue

    try:
        with Image.open(file_path) as img:
            # Get the mode string
            mode = img.mode
            
            # Increment the count. If the mode isn't in the dict yet, default to 0 and add 1
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

    except Image.UnidentifiedImageError:
        num_unidentified += 1

# Print the results sorted from most to least common
print("Image Modes:")
for mode, count in sorted(mode_counts.items(), key=lambda item: item[1], reverse=True):
    print(f"Mode {mode}: {count} images")

print(f"Unidentified/Non-images: {num_unidentified}")