from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import fitz  # PyMuPDF
import img2pdf
from PIL import Image
from ..database import get_db_connection

router = APIRouter()

def convert_to_pdf(file_path: str) -> str:
    """Converts DOCX or Images to PDF if necessary, returning the new path"""
    if file_path.lower().endswith('.pdf'):
        return file_path
    
    pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
    
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Convert image to PDF
        image = Image.open(file_path)
        # Convert to RGB if PNG has alpha channel
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        temp_img_path = file_path + "_temp.jpg"
        image.save(temp_img_path)
        
        pdf_bytes = img2pdf.convert(temp_img_path)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        os.remove(temp_img_path)
        return pdf_path
    elif file_path.lower().endswith('.docx'):
        # For simplicity, docx conversion via LibreOffice headless
        import subprocess
        try:
            # On Windows, soffice must be in PATH. On Linux, it's usually available.
            cmd = ['soffice', '--headless', '--convert-to', 'pdf', file_path, '--outdir', os.path.dirname(file_path)]
            subprocess.run(cmd, check=True)
            return pdf_path
        except Exception as e:
            raise HTTPException(status_code=500, detail="Could not convert DOCX to PDF. Ensure LibreOffice is installed and in PATH.")
    
    return file_path

@router.get("/{job_id}")
async def get_preview(job_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
        
    original_path = row['file_path']
    try:
        pdf_path = convert_to_pdf(original_path)
    except Exception as e:
        conn.close()
        raise e

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Invalid PDF file")

    total_pages = len(doc)
    thumbnails = []

    num_previews = min(3, total_pages)
    job_dir = os.path.dirname(pdf_path)
    
    for i in range(num_previews):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        thumb_path = os.path.join(job_dir, f"thumb_{i}.png")
        pix.save(thumb_path)
        thumbnails.append(f"/preview/{job_id}/thumb/{i}")

    cursor.execute("""
        UPDATE jobs SET total_pages = ?, file_path = ? WHERE job_id = ?
    """, (total_pages, pdf_path, job_id))
    conn.commit()
    conn.close()
    
    return {
        "job_id": job_id,
        "total_pages": total_pages,
        "thumbnails": thumbnails
    }

@router.get("/{job_id}/thumb/{page_idx}")
async def get_thumbnail(job_id: str, page_idx: int):
    thumb_path = os.path.join("tmp", "kiosk_jobs", job_id, f"thumb_{page_idx}.png")
    if not os.path.exists(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumb_path, media_type="image/png")
