import os
import extractor as ex
import image_processing as ip

def run_pipeline(pdf_path: str, output_dir: str):
    print(f"Starting extraction for {pdf_path}...")
    
    meta_stream = ex.get_image_metadata(pdf_path)
    img_stream = ex.extract_pillow_images(pdf_path, meta_stream)
    
    for meta, pil_img in img_stream:
        
        target_folder = os.path.join(output_dir)
        os.makedirs(target_folder, exist_ok=True)
        
        filename = f"page_{meta['page_number']}_{meta['xref']}.{ext}"
        with open(os.path.join(target_folder, filename), "wb") as f:
            f.write(pil_img)

if __name__ == "__main__":
    run_pipeline("test.pdf", "test_output")