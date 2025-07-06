import fitz
import os
from typing import List

def pdf_to_images(pdf_path: str, output_dir: str) -> List[str]:
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(output_dir, f"page_{page_num+1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
    return image_paths 