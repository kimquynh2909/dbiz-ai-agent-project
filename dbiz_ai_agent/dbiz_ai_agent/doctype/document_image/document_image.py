# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
from datetime import datetime
from PIL import Image
import base64
from frappe.utils import get_url


_IMAGE_LIST_FIELDS = [
	"name",
	"title",
	"description",
	"image_file",
	"image_type",
	"parent_document",
	"page_number",
	"extracted_text",
	"alt_text",
	"tags",
	"dimensions",
	"file_size",
	"category",
]


class DocumentImage(Document):
	def before_insert(self):
		if not self.extracted_date:
			self.extracted_date = datetime.now()
		self.set_image_metadata()

	def set_image_metadata(self):
		file_path = _resolve_file_path(self.image_file)
		if not file_path:
			return

		self.file_size = _format_file_size(os.path.getsize(file_path))
		try:
			with Image.open(file_path) as img:
				self.dimensions = f"{img.width}x{img.height}"
		except Exception:
			self.dimensions = "Unknown"

	def get_image_base64(self):
		file_path = _resolve_file_path(self.image_file)
		if not file_path:
			return None
		try:
			with open(file_path, 'rb') as img_file:
				return base64.b64encode(img_file.read()).decode('utf-8')
		except Exception:
			return None
	
@frappe.whitelist()
def get_document_images(document_name):
	"""Get all images for a specific document"""
	return _get_images(
		{"parent_document": document_name},
		order_by="page_number ASC, position_in_document ASC",
	)


@frappe.whitelist()
def get_image_with_context(image_name):
	"""Get image with full context for chatbot responses"""
	try:
		image_doc = frappe.get_doc("Document Image", image_name)
		parent_meta = frappe.db.get_value(
			"AI Document",
			image_doc.parent_document,
			["title", "category"],
			as_dict=True,
		)
		image_base64 = image_doc.get_image_base64()
		image_info = _build_image_payload(image_doc.as_dict())
		
		return {
			"image_info": {
				"name": image_info.get("id"),
				"title": image_info.get("title"),
				"description": image_info.get("description"),
				"image_type": image_info.get("image_type"),
				"category": image_info.get("category"),
				"dimensions": image_info.get("dimensions"),
				"file_size": image_info.get("file_size"),
			},
			"document_context": {
				"document_title": parent_meta.title if parent_meta else None,
				"document_category": parent_meta.category if parent_meta else None,
				"page_number": image_info.get("page_number"),
				"position": image_doc.position_in_document,
			},
			"content": {
				"extracted_text": image_doc.extracted_text,
				"alt_text": image_doc.alt_text,
				"surrounding_text": image_doc.surrounding_text,
				"image_context": image_doc.image_context,
				"tags": image_doc.tags,
			},
			"image_data": {
				"url": image_info.get("file_url"),
				"base64": image_base64,
			},
		}
	except Exception as e:
		frappe.log_error(f"Error getting image with context: {str(e)}")
		return None


@frappe.whitelist()
def search_images_by_content(query, document_name=None):
	"""Search images by content, text, or context"""
	filters = {}
	if document_name:
		filters["parent_document"] = document_name
	if not (query or "").strip():
		return _get_images(
			filters,
			order_by="parent_document ASC, page_number ASC",
			limit=20,
		)

	# Search in multiple fields
	or_filters = [
		{"title": ["like", f"%{query}%"]},
		{"description": ["like", f"%{query}%"]},
		{"extracted_text": ["like", f"%{query}%"]},
		{"alt_text": ["like", f"%{query}%"]},
		{"image_context": ["like", f"%{query}%"]},
		{"tags": ["like", f"%{query}%"]}
	]

	images_by_name = {}
	for condition in or_filters:
		combined_filters = {**filters, **condition}
		for row in _get_images(
			combined_filters,
			order_by="parent_document ASC, page_number ASC",
		):
			images_by_name[row.name] = row

	return list(images_by_name.values())[:20]



def fetch_images_from_placeholders(placeholders, seen_placeholders=None, *, parent_document: str | None = None, skip_numeric: bool = False):
    """Resolve placeholder identifiers về payload hình ảnh.

    - If skip_numeric is True, numeric-only identifiers like "1", "2" are ignored because
      these are ambiguous across different documents (alt_text is not globally unique).
    - If parent_document is provided and identifier is numeric, we scope resolution to the
      given document to avoid cross-document collisions.
    """
    if seen_placeholders is None:
        seen_placeholders = set()

    collected = []
    for raw in placeholders:
        identifier = (raw or "").strip()
        if not identifier:
            continue

        # Normalize for comparison only; we still pass the original identifier to resolver
        ident_str = str(identifier)
        if skip_numeric and ident_str.isdigit():
            # Defer numeric placeholder resolution until final metadata is available
            # (e.g. via tool results) to avoid mixing images from other documents.
            continue

        keys_to_mark = _placeholder_keys(ident_str)
        if any(key in seen_placeholders for key in keys_to_mark):
            continue

        image_payload = resolve_image_by_identifier(ident_str, parent_document=parent_document)
        if image_payload:
            collected.append(image_payload)
            seen_placeholders.update(keys_to_mark)

    return collected


def resolve_image_by_identifier(identifier, *, parent_document: str | None = None):
    image_row = _resolve_image_row(identifier, parent_document=parent_document)
    if not image_row:
        return None
    return _build_image_payload(image_row)


def _get_images(filters=None, *, fields=None, order_by=None, limit=None):
	filters = filters or {}
	query_fields = fields or _IMAGE_LIST_FIELDS
	return frappe.get_all(
		"Document Image",
		filters=filters,
		fields=query_fields,
		order_by=order_by,
		limit=limit,
	)


def _resolve_image_row(identifier, *, parent_document: str | None = None):
    lookups = []
    # First prefer direct name match
    lookups.append({"name": identifier})
    # Then alt_text match (exact token)
    alt_token = f"[[IMAGE::{identifier}]]"
    if parent_document:
        lookups.append({"alt_text": alt_token, "parent_document": parent_document})
    lookups.append({"alt_text": alt_token})
    # If identifier is purely numeric, optional extra lookup with normalized int
    if identifier.isdigit():
        normalized = f"[[IMAGE::{int(identifier)}]]"
        if parent_document:
            lookups.append({"alt_text": normalized, "parent_document": parent_document})
        lookups.append({"alt_text": normalized})

    fields = [
        "name", "title", "image_file", "parent_document", "page_number", "description",
        "alt_text", "image_type", "category", "dimensions", "file_size"
    ]

    for lookup in lookups:
        row = frappe.db.get_value("Document Image", lookup, fields, as_dict=True)
        if row:
            return row
    return None


def _build_image_payload(image_data):
	data = frappe._dict(image_data)
	file_url = data.get("image_file")
	absolute_url = file_url
	if file_url and not file_url.lower().startswith(("http://", "https://")):
		absolute_url = get_url(file_url)

	return {
		"id": data.get("name"),
		"title": data.get("title"),
		"image_url": absolute_url,
		"file_url": file_url,
		"parent_document": data.get("parent_document"),
		"page_number": data.get("page_number"),
		"description": data.get("description"),
		"alt_text": data.get("alt_text"),
		"image_type": data.get("image_type"),
		"category": data.get("category"),
		"dimensions": data.get("dimensions"),
		"file_size": data.get("file_size"),
	}


def _placeholder_keys(identifier):
	normalized = identifier.upper()
	alt_key = f"[[IMAGE::{identifier}]]"
	return {normalized, alt_key}


def _resolve_file_path(file_url):
	if not file_url:
		return None
	try:
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		full_path = file_doc.get_full_path()
		if os.path.exists(full_path):
			return full_path
	except frappe.DoesNotExistError:
		return None
	except Exception as err:
		frappe.log_error(f"Unable to resolve file path for {file_url}: {str(err)}")
	return None


def _format_file_size(size_in_bytes):
	units = ["B", "KB", "MB", "GB", "TB"]
	value = float(size_in_bytes)
	for unit in units:
		if value < 1024 or unit == units[-1]:
			return f"{value:.2f} {unit}"
		value /= 1024
