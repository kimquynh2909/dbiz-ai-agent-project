from dbiz_ai_agent.agentic_ai.tools.document_tools import DocumentProcessingTools
import frappe
from frappe import _
import os
import base64
import mimetypes
from datetime import datetime
from dbiz_ai_agent.api.document_permissions import check_document_access
from dbiz_ai_agent.integrations import qdrant_store
from frappe.utils.data import now_datetime
from frappe.utils.file_manager import save_file
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

@frappe.whitelist()
def get_documents(folder_id=None):
    """Get all documents for current user, optionally filtered by folder and permissions"""
    current_user = frappe.session.user
    if folder_id:
        filters = {"folder_id": folder_id}
    else:
        filters = {"folder_id": ["is", "not set"]}

    docs = [
        frappe.get_doc("AI Document", d.name).as_dict()
        for d in frappe.get_all("AI Document", filters=filters, order_by="upload_date desc")
        if check_document_access(d.name, current_user)
    ]

    return [
        {
            'id': doc.name,
            'title': doc.title,
            'category': doc.category,
            'status': doc.status,
            'size': doc.file_size,
            'fileType': doc.file_type or '',
            'uploadedBy': doc.uploaded_by,
            'uploadDate': doc.upload_date,
            'description': doc.description,
            'tags': doc.tags,
            'fileUrl': doc.file_attachment,
            'folder_id': doc.folder_id
        }
        for doc in docs
    ]

@frappe.whitelist()
def get_folders(parent_folder_id=None):
    """Get all folders, optionally filtered by parent folder"""
    filters = {}
    if parent_folder_id:
        filters["parent_folder_id"] = parent_folder_id
    else:
        filters["parent_folder_id"] = ["is", "not set"]
    
    folders = frappe.get_all(
        "AI Folder",
        filters=filters,
        fields=[
            "name as id",
            "folder_name as name",
            "description",
            "created_at as createdAt",
            "parent_folder_id"
        ],
        order_by="folder_name asc"
    )
    
    # Add item count for each folder
    for folder in folders:
        # Count documents in this folder
        doc_count = frappe.db.count("AI Document", {"folder_id": folder["id"]})
        # Count subfolders
        subfolder_count = frappe.db.count("AI Folder", {"parent_folder_id": folder["id"]})
        folder["itemCount"] = doc_count + subfolder_count
    
    return folders


@frappe.whitelist()
def get_all_folders():
    """Return all folders (flat list) so frontend can build trees or dropdowns with nested folders."""
    folders = frappe.get_all(
        "AI Folder",
        fields=[
            "name as id",
            "folder_name as name",
            "description",
            "created_at as createdAt",
            "parent_folder_id"
        ],
        order_by="folder_name asc"
    )

    # Add item count for each folder
    for folder in folders:
        doc_count = frappe.db.count("AI Document", {"folder_id": folder["id"]})
        subfolder_count = frappe.db.count("AI Folder", {"parent_folder_id": folder["id"]})
        folder["itemCount"] = doc_count + subfolder_count

    return folders

@frappe.whitelist()
def create_folder(name, description="", parent_folder_id=None):
    """Create a new folder"""
    try:
        # Validate folder name
        if not name or not name.strip():
            frappe.throw(_("Folder name is required"))
        
        # Check if folder with same name exists in same parent
        existing_filters = {"folder_name": name.strip()}
        if parent_folder_id:
            existing_filters["parent_folder_id"] = parent_folder_id
        else:
            existing_filters["parent_folder_id"] = ["is", "not set"]
        
        existing = frappe.get_all("AI Folder", filters=existing_filters, limit=1)
        if existing:
            frappe.throw(_("A folder with this name already exists in this location"))
        
        # Create folder
        folder = frappe.get_doc({
            "doctype": "AI Folder",
            "folder_name": name.strip(),
            "description": description.strip(),
            "parent_folder_id": parent_folder_id,
            "created_by": frappe.session.user
        })
        folder.insert()
        
        return {
            "id": folder.name,
            "name": folder.folder_name,
            "description": folder.description,
            "createdAt": folder.creation,
            "itemCount": 0
        }
        
    except Exception as e:
        frappe.throw(_("Error creating folder: {0}").format(str(e)))

@frappe.whitelist()
def rename_folder(folder_id, new_name):
    """Rename a folder"""
    try:
        # Validate new name
        if not new_name or not new_name.strip():
            frappe.throw(_("Folder name cannot be empty"))
        
        folder = frappe.get_doc("AI Folder", folder_id)
        
        # Check permissions
        if folder.created_by != frappe.session.user and not frappe.has_permission("AI Folder", "write"):
            frappe.throw(_("You don't have permission to rename this folder"))
        
        # Check if folder with same name exists in same parent
        existing_filters = {
            "folder_name": new_name.strip(),
            "name": ["!=", folder_id]
        }
        if folder.parent_folder_id:
            existing_filters["parent_folder_id"] = folder.parent_folder_id
        else:
            existing_filters["parent_folder_id"] = ["is", "not set"]
        
        existing = frappe.get_all("AI Folder", filters=existing_filters, limit=1)
        if existing:
            frappe.throw(_("A folder with this name already exists in this location"))
        
        # Update folder name
        folder.folder_name = new_name.strip()
        folder.flags.ignore_version_check = True
        folder.save()
        
        return {
            "success": True,
            "id": folder.name,
            "name": folder.folder_name
        }
        
    except Exception as e:
        frappe.throw(_("Error renaming folder: {0}").format(str(e)))

@frappe.whitelist()
def delete_folder(folder_id):
    """Delete a folder and all its contents"""
    try:
        folder = frappe.get_doc("AI Folder", folder_id)
        
        # Check permissions
        if folder.created_by != frappe.session.user and not frappe.has_permission("AI Folder", "delete"):
            frappe.throw(_("You don't have permission to delete this folder"))
        
        # Check if folder has contents
        doc_count = frappe.db.count("AI Document", {"folder_id": folder_id})
        subfolder_count = frappe.db.count("AI Folder", {"parent_folder_id": folder_id})
        
        if doc_count > 0 or subfolder_count > 0:
            frappe.throw(_("Cannot delete folder that contains documents or subfolders"))
        
        # Delete folder
        folder.delete()
        
        return {"success": True}
        
    except Exception as e:
        frappe.throw(_("Error deleting folder: {0}").format(str(e)))

def crawl_web_content(url, description=""):
    """
    Crawl content from a web URL
    Returns: (content_text, title)
    """
    try:
        # Add timeout and headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get page title
        page_title = soup.title.string if soup.title else urlparse(url).netloc
        
        # Extract text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Prepare final content
        content = f"Source URL: {url}\n"
        if description:
            content += f"\nDescription: {description}\n"
        content += f"\nPage Title: {page_title}\n"
        content += f"\n{'='*80}\n\n"
        content += text
        
        return content, page_title
    
    except Exception as e:
        frappe.log_error(f"Web crawl error for {url}: {str(e)}", "Web Crawl Error")
        return f"Failed to crawl content from {url}\nError: {str(e)}", "Crawl Failed"

@frappe.whitelist()
def upload_document():
    fd = frappe.form_dict
    if not (fd.get("title") and fd.get("category")):
        frappe.throw(_("Missing required fields: title, category"))

    # Check if this is a URL import
    url = fd.get("url")
    
    uploaded = None
    if frappe.request and getattr(frappe.request, "files", None):
        uploaded = frappe.request.files.get("file")

    file_name = None
    file_type = None
    file_content = None
    decode_content = False

    if uploaded:
        file_name = uploaded.filename or fd.get("file_name")
        file_type = uploaded.content_type
        file_content = uploaded.stream.read()
        decode_content = False
    elif fd.get("file"):
        file_name = fd.get("file_name")
        b64 = fd.file.split(",", 1)[1] if "," in fd.file else fd.file
        file_content = b64
        decode_content = True
        file_type = fd.get("file_type")
    elif url:
        # URL import - crawl content from the URL
        url_description = fd.get("description", "")
        crawled_content, page_title = crawl_web_content(url, url_description)
        
        # Use page title as filename if no title provided
        safe_filename = fd.get('title', page_title).replace(' ', '_').replace('/', '_')
        file_name = f"{safe_filename}_web_content.txt"
        file_type = "text/plain"
        file_content = crawled_content.encode('utf-8')
        decode_content = False

    if not file_content and not url:
        frappe.throw(_("Missing file to upload or URL to import"))

    if not file_name:
        frappe.throw(_("File name is required"))

    if not file_type:
        guess = mimetypes.guess_type(file_name)[0]
        file_type = guess or ""

    # Do not pass AI Folder id to save_file's "folder" parameter — it expects a File folder/path.
    # Passing the AI Folder id caused LinkValidationError: Could not find Folder: <id>
    f = save_file(file_name, file_content, None, None, folder=None, decode=decode_content, is_private=0)

    cat_map = {"faq":"FAQ","guide":"Guide","policy":"Policy","technical":"Technical",
               "software":"Software","hardware":"Hardware","other":"Other"}
    cat = cat_map.get(fd.get("category","").lower(), "Other")

    doc_data = {
        "doctype": "AI Document",
        "title": fd.title,
        "category": cat,
        "description": fd.get("description",""),
        "tags": fd.get("tags",""),
        "file_attachment": f.file_url,
        "file_size": f"{f.file_size} bytes",
        "file_type": file_type,
        "uploaded_by": frappe.session.user,
        "upload_date": now_datetime(),
        "status": "Processing",
        "folder_id": fd.get("folder_id"),
        "access_level": fd.get("access_level","Internal"),
        "roles_allowed": fd.get("roles_allowed",""),
        "departments_allowed": fd.get("departments_allowed",""),
    }
    
    # If this is a URL import, store the source URL
    if url:
        doc_data["source_url"] = url
    
    doc = frappe.get_doc(doc_data).insert(ignore_permissions=True)
    f = frappe.get_doc("File", f.name)
    f.attached_to_doctype = "AI Document"
    f.attached_to_name = doc.name
    f.save(ignore_permissions=True)

    frappe.enqueue(
        process_document_background,
        queue="default", 
        timeout=1800,  # 30 minutes for large files (200MB+)
        document_id=doc.name,
        file_path=frappe.get_site_path("public", f.file_url.lstrip("/"))
    )

    return {
        "id": doc.name, "title": doc.title, "category": doc.category, "status": doc.status,
        "size": doc.file_size, "uploadedBy": doc.uploaded_by, "uploadDate": doc.upload_date,
        "fileUrl": doc.file_attachment
    }
    
    
def process_document_background(document_id, file_path):
    try:
        doc = frappe.get_doc("AI Document", document_id)
        file_name = os.path.basename(file_path)
        corrected_file_path = frappe.get_site_path("public", "files", file_name)
        
        if not os.path.exists(corrected_file_path):
            raise Exception(f"File not found: {corrected_file_path}")
        
        doc_tools = DocumentProcessingTools()
        result = doc_tools.process_document(corrected_file_path, document_id)

        doc.status = "Processed"
        doc.content = result.get("full_text", "")
        doc.chunks_count = result.get("chunks_count", 0)
        doc.processed_date = frappe.utils.now()
        
        ai_desc = result.get("ai_description", "")
        ai_keywords = result.get("ai_keywords", "")
        
        if ai_desc:
            if doc.description and doc.description.strip():
                doc.description = doc.description.strip() + "\n\n[AI Generated]: " + ai_desc
            else:
                doc.description = ai_desc
        
        if ai_keywords:
            if doc.tags and doc.tags.strip():
                existing_tags = doc.tags.strip()
                separator = ", " if not existing_tags.endswith(",") else ""
                doc.tags = existing_tags + separator + ai_keywords
            else:
                doc.tags = ai_keywords
        
        doc.save()
        frappe.db.commit()
        
    except Exception as e:
        error_msg = str(e)[:500]  
        # Try to mark the document as errored using an allowed status value.
        try:
            doc = frappe.get_doc("AI Document", document_id)
            doc.status = "Error"
            doc.error_message = error_msg
            # Use ignore_permissions and save safely to avoid raising validation errors
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception as save_exc:
            # Log failure to persist the error state but do not re-raise — avoid flooding logs
            frappe.log_error(f"Failed to persist error status for document {document_id}: {str(save_exc)}")
        # Also log the original processing error for diagnostics
        frappe.log_error(f"Document processing failed for {document_id}: {error_msg}")

@frappe.whitelist(allow_guest=True)
def move_document(document_id, target_folder_id=None):
    """Move a document to another folder"""
    try:
        doc = frappe.get_doc("AI Document", document_id)
        
        # Check permissions
        if doc.uploaded_by != frappe.session.user and not frappe.has_permission("AI Document", "write"):
            frappe.throw(_("You don't have permission to move this document"))
        
        # Validate target folder if provided
        if target_folder_id:
            target_folder = frappe.get_doc("AI Folder", target_folder_id)
            if not target_folder:
                frappe.throw(_("Target folder not found"))
        
        # Update document folder
        old_folder_id = doc.folder_id
        doc.folder_id = target_folder_id
        doc.save()
        
        return {
            "success": True,
            "message": _("Document moved successfully"),
            "old_folder_id": old_folder_id,
            "new_folder_id": target_folder_id
        }
        
    except Exception as e:
        frappe.log_error(f"Document move error: {str(e)}")
        frappe.throw(_("Error moving document: {0}").format(str(e)))

@frappe.whitelist()
def delete_document(document_id):
    """Delete a document and clean up related assets (files, images, vectors)."""
    try:
        current_user = frappe.session.user
        
        # Check permissions using helper function
        if not check_document_access(document_id, current_user):
            return {"success": False, "error": _("You don't have permission to delete this document")}
        
        doc = frappe.get_doc("AI Document", document_id)
        
        # Additional check: only owner or admin can delete
        if (doc.owner != current_user and doc.uploaded_by != current_user) and current_user != "Administrator":
            return {"success": False, "error": _("Only the document owner or Administrator can delete this document")}

        # Remove vectors from Qdrant
        try:
            qdrant_store.delete_document(doc.name)
        except Exception as err:
            frappe.log_error(f"Qdrant cleanup failed for {doc.name}: {str(err)}")

        # Delete extracted images and their files
        try:
            images = frappe.get_all(
                "Document Image",
                filters={"parent_document": doc.name},
                fields=["name", "image_file"],
            )
            for image in images:
                image_file_url = image.get("image_file")
                if image_file_url:
                    try:
                        file_doc = frappe.get_doc("File", {"file_url": image_file_url})
                        file_doc.delete(ignore_permissions=True)
                    except Exception as file_err:
                        frappe.log_error(f"Failed to delete image file {image_file_url}: {str(file_err)}")

                try:
                    img_doc = frappe.get_doc("Document Image", image["name"])
                    img_doc.delete(ignore_permissions=True)
                except Exception as img_err:
                    frappe.log_error(f"Failed to delete Document Image {image.get('name')}: {str(img_err)}")
        except Exception as err:
            frappe.log_error(f"Error while cleaning document images for {doc.name}: {str(err)}")

        # Delete associated files (primary attachment + any linked File records)
        file_urls = set()
        if doc.get("file_attachment"):
            file_urls.add(doc.file_attachment)
        if getattr(doc, "file_url", None):
            file_urls.add(doc.file_url)

        try:
            attached_files = frappe.get_all(
                "File",
                filters={"attached_to_doctype": "AI Document", "attached_to_name": doc.name},
                pluck="name",
            )
        except Exception:
            attached_files = []

        for file_url in file_urls:
            try:
                if not frappe.db.exists("File", {"file_url": file_url}):
                    continue
                file_doc = frappe.get_doc("File", {"file_url": file_url})
                file_doc.delete(ignore_permissions=True)
            except Exception as file_err:
                frappe.log_error(f"Failed to delete file {file_url}: {str(file_err)}")

        for file_name in attached_files:
            try:
                if not frappe.db.exists("File", file_name):
                    continue
                file_doc = frappe.get_doc("File", file_name)
                file_doc.delete(ignore_permissions=True)
            except Exception as file_err:
                frappe.log_error(f"Failed to delete attached file {file_name}: {str(file_err)}")
        
        # Delete document
        doc.delete()
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Document delete error: {str(e)}")
        return {"success": False, "error": _("Error deleting document: {0}").format(str(e))}
