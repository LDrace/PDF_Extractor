import utils
import os
import pymupdf as pdf
import time

import image_processing as ip
import extractor as ex
import gemini_scores as gs

from PIL import Image

output_dir = "./output"

start_time = time.perf_counter()

raw_metadata = ip.get_image_metadata("test.pdf", log=0)
unique_metadata = ip.check_xref_duplicates(raw_metadata)
analyzed_metadata = ip.meta_analysis(unique_metadata, log=0)

img_stream = ex.extract_pillow_images("test.pdf", analyzed_metadata)

os.makedirs(output_dir, exist_ok=True)

count = 0

for meta, img, ext, img_bytes in img_stream:
        count += 1
        
        # Verify the dimensions inside the PIL object line up with our metadata
        # (This confirms our .load() handoff was completely successful)
        print(f"Processing image {count} (XREF: {meta['xref']}) -> Format: {ext.upper()} | Dimensions: {img.size}")
        
        filename = f"page_{meta['page_number']}_{meta['xref']}.{ext}"
        full_path = os.path.join(output_dir, filename)
        
        # In-place write using the exact binary stream
        with open(full_path, "wb") as f:
            f.write(img_bytes)

print(f"\nSuccess! Successfully extracted {count} assets into '{output_dir}/'.")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Extraction and analysis completed in {elapsed_time:.6f}.")

summarized_metadata = gs.analyze_score_distribution(analyzed_metadata)
processed_images = list(summarized_metadata)