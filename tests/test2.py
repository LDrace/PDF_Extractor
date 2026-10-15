import extract.utils as utils
import os
import pymupdf as pdf
import time

import extract.extractor as ex
import extract.image_processing as ip
import tests.gemini_scores as gs

from PIL import Image

output_dir = "./output"

start_time = time.perf_counter()

raw_metadata = ex.get_image_metadata("test.pdf", log=0)
unique_metadata = ip.check_xref_duplicates(raw_metadata)
analyzed_metadata = ip.meta_analysis(unique_metadata, log=0)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Extraction and analysis completed in {elapsed_time:.6f}.")

summarized_metadata = gs.analyze_score_distribution(analyzed_metadata)
processed_images = list(summarized_metadata)