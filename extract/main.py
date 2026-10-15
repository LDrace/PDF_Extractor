import os

from .extractor import get_image_metadata, extract_pillow_images

def run_pipeline(pdf_path: str, output_dir: str, show_count:bool = False):
    print(f"Starting extraction for {pdf_path}...")
    
    meta_stream = get_image_metadata(pdf_path)
    img_stream = extract_pillow_images(pdf_path, meta_stream)

    if show_count:
        image_count = 0
    
    for meta, pil_img, ext, img_bytes in img_stream:
        
        target_folder = os.path.join(output_dir)
        os.makedirs(target_folder, exist_ok=True)
        
        filename = f"page_{meta['page_number']}_{meta['xref']}.{ext}"
        with open(os.path.join(target_folder, filename), "wb") as f:
            f.write(img_bytes)

        if show_count:
            image_count += 1
            print(f"\rExtracted {image_count} images...", end="", flush=True)

if __name__ == "__main__":
    input_path = input("Please enter the path to the PDF you wish to extract images from: ")
    output_path = input("Please enter the path you would like the extracted images to be saved to: ")

    run_pipeline(input_path, output_path, show_count=True)

    print("\nExtraction complete.")