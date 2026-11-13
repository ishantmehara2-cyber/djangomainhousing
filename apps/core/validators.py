import os
from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.svg']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.webp']

def validate_file_size_5mb(uploaded_file):
    """
    Strictly validates that any uploaded file does not exceed 5 MB (5,242,880 bytes).
    """
    if uploaded_file and hasattr(uploaded_file, 'size') and uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
        size_mb = uploaded_file.size / (1024 * 1024)
        raise ValidationError(f"Maximum allowed file size is 5 MB per file. Uploaded file size is {size_mb:.2f} MB.")
    return uploaded_file

def validate_document_file(uploaded_file):
    """
    Validates document file size (5MB) and permitted file extensions (PDF, JPG, PNG, WEBP).
    """
    validate_file_size_5mb(uploaded_file)
    if uploaded_file and hasattr(uploaded_file, 'name'):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise ValidationError(f"Unsupported file format '{ext}'. Allowed document formats are: PDF, JPG, JPEG, PNG, WEBP.")
    return uploaded_file

def validate_image_file(uploaded_file):
    """
    Validates image file size (5MB) and permitted image extensions (JPG, PNG, WEBP, SVG).
    """
    validate_file_size_5mb(uploaded_file)
    if uploaded_file and hasattr(uploaded_file, 'name'):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"Unsupported image format '{ext}'. Allowed formats are: JPG, JPEG, PNG, WEBP, SVG.")
    return uploaded_file
