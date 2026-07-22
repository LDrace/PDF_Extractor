import sys
import os
import io
import pymupdf as pdf
from PIL import Image

def extract_img_ref(pdf_path, output_dir):
    """
    Extracts all images from a PDF and saves them to an output directory.
    """
    # 1. Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 2. Open the PDF document
    doc = pdf.open(pdf_path)
    
    image_count = 0

    # 3. Iterate through every page
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get a list of images on this specific page
        # full=True ensures we get the actual image, not a thumbnail/mask
        image_list = page.get_images(full=True)
        
        if not image_list:
            continue
            
        print(f"Found {len(image_list)} image(s) on page {page_num + 1}")
        
        # 4. Iterate through the images found on the page
        for img_index, img_info in enumerate(image_list):
            # The xref is always the first item in the img_info tuple
            xref = img_info[0]
            
            # Extract the raw image dictionary using the xref
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"] # e.g., 'png', 'jpeg'
            
            # 5. Load the bytes into Pillow
            try:
                img = Image.open(io.BytesIO(image_bytes))
                
                # Create a clean filename
                image_count += 1
                filename = f"image_{image_count:03d}.{image_ext}"
                filepath = os.path.join(output_dir, filename)
                
                # Save the file
                img.save(filepath)
                print(f"  Saved: {filename}")
                
            except Exception as e:
                print(f"  Error processing image {xref} on page {page_num + 1}: {e}")

    print(f"\nFinished! Extracted {image_count} total images.")
    doc.close()

if __name__ == "__main__":
    pdf1 = input("Paste the file path for the PDF you would like to extract from:") or "test.pdf"
    extraction_folder = input("Paste the file path for the folder you would like the images extracted into:") or "./output"
    extract_img_ref(pdf1, extraction_folder)