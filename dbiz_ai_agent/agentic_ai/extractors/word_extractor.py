"""
Word Extractor - Extract text and images from Word documents
"""
import os
import subprocess
import tempfile
import frappe
from typing import Dict, List, Any, Optional

from ..utils.image_utils import save_image


def _convert_doc_to_docx(src_path: str) -> str:
    """
    Convert various document formats to DOCX using LibreOffice.
    
    Supports: .doc, .docm, .dot, .dotx, .dotm, .odt, .ott, .sxw, .rtf, .wps
    
    Args:
        src_path: Path to source document
    
    Returns:
        Path to converted DOCX file
    """
    if not os.path.exists(src_path):
        raise Exception(f"Source file not found: {src_path}")
    
    tmpdir = tempfile.mkdtemp(prefix="doc_convert_")
    
    try:
        # Find LibreOffice executable
        lo_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
            "/usr/bin/soffice",  # Linux
            "/usr/local/bin/soffice",  # Linux alternative
        ]
        lo_cmd = None
        for path in lo_paths:
            if os.path.exists(path):
                lo_cmd = path
                break
        
        if not lo_cmd:
            raise Exception("LibreOffice not found. Please install LibreOffice.")
        
        proc = subprocess.run(
            [lo_cmd, "--headless", "--convert-to", "docx", "--outdir", tmpdir, src_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
        
        if proc.returncode != 0:
            raise Exception(
                f"Conversion failed: stdout={proc.stdout.decode('utf-8', 'ignore')}; "
                f"stderr={proc.stderr.decode('utf-8', 'ignore')}"
            )
        
        base = os.path.splitext(os.path.basename(src_path))[0]
        candidate = os.path.join(tmpdir, base + ".docx")
        
        if os.path.exists(candidate):
            return candidate
        
        for fname in os.listdir(tmpdir):
            if fname.lower().endswith(".docx"):
                return os.path.join(tmpdir, fname)
        
        raise Exception("Conversion did not produce a .docx file")
    except Exception as err:
        frappe.log_error(f"DOC->DOCX conversion failed: {str(err)}")
        raise


def extract_from_word(word_path: str, document_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract text and images from Word documents (DOCX), keeping image positions in text.
    
    Args:
        word_path: Path to the Word document
        document_name: AI Document name for tracking
    
    Returns:
        Dictionary containing:
        - text: Extracted text with image placeholders
        - images: List of extracted image metadata
        - document_id: Document identifier
    """
    try:
        import docx
    except ImportError:
        from .text_extractor import extract_from_text
        text_content = extract_from_text(word_path)
        return {"text": text_content.get("text", ""), "images": [], "document_id": document_name}
    
    resolved_path = word_path
    if not os.path.exists(resolved_path):
        try_path = frappe.get_site_path("public", "files", os.path.basename(word_path))
        if os.path.exists(try_path):
            resolved_path = try_path
    
    if not os.path.exists(resolved_path):
        raise Exception(f"Word file not found at '{word_path}'")
    
    lower_ext = os.path.splitext(resolved_path)[1].lower()
    
    # Convert các định dạng document khác sang DOCX
    if lower_ext in [".doc", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".ott", ".sxw", ".rtf", ".wps"]:
        resolved_path = _convert_doc_to_docx(resolved_path)
    
    doc = docx.Document(resolved_path)
    all_text_parts: List[str] = []
    images_output: List[Dict[str, Any]] = []
    parent_document: Optional[str] = document_name
    img_count = 0
    
    for block in doc.element.body.iterchildren():
        if block.tag.endswith("}p"):
            para = docx.text.paragraph.Paragraph(block, doc)
            para_text_parts: List[str] = []
            
            for run in para.runs:
                if run.text:
                    para_text_parts.append(run.text)
                
                blip_embeds = run.element.xpath(".//a:blip/@r:embed")
                for rId in blip_embeds:
                    img_rel = doc.part.rels.get(rId)
                    if not img_rel:
                        continue
                    
                    img_count += 1
                    image_bytes = getattr(img_rel.target_part, "blob", None)
                    if not image_bytes:
                        continue
                    
                    target = getattr(img_rel, "target_ref", "") or ""
                    lower = target.lower()
                    
                    if lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff")):
                        filename = f"{document_name}_{os.path.basename(target)}"
                    else:
                        filename = f"{document_name}_{img_count}.png"
                    
                    file_url, doc_image = save_image(
                        image_bytes,
                        filename,
                        is_private=0,
                        parent_document=parent_document,
                        page_number=None,
                        position=f"{img_count}",
                    )
                    
                    # Use Document Image id as token if available (e.g. IMG-12345)
                    placeholder = f"[[IMAGE::{doc_image}]]"
                    para_text_parts.append(placeholder)
                    images_output.append({
                        "id": placeholder,
                        "file_url": file_url,
                        "document_image": doc_image,
                        "parent_document": parent_document,
                    })
            
            para_text = "".join(para_text_parts).strip()
            if para_text:
                all_text_parts.append(para_text)
                all_text_parts.append("\n")
    
    full_text = "".join(all_text_parts).strip()
    
    return {
        "text": full_text,
        "images": images_output,
        "document_id": parent_document,
    }

