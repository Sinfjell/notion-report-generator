import os
from pathlib import Path
from typing import Union
from .settings import settings

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


def upload_text_local(file_path: str, text: str) -> str:
    """
    Upload text content to local file system.
    
    Args:
        file_path: Path where to save the file
        text: Text content to upload
        
    Returns:
        Local file path
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write text content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return f"file://{os.path.abspath(file_path)}"


def upload_text_public(bucket_name: str, blob_path: str, text: str) -> str:
    """
    Upload text content to Google Cloud Storage as a public object.
    
    Args:
        bucket_name: Name of the GCS bucket
        blob_path: Path within the bucket for the blob
        text: Text content to upload
        
    Returns:
        Public URL of the uploaded blob
    """
    if not GCS_AVAILABLE:
        raise ImportError("google-cloud-storage not available")
    
    # Initialize the GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Create blob
    blob = bucket.blob(blob_path)
    
    # Upload text content with UTF-8 encoding
    blob.upload_from_string(text, content_type='text/plain; charset=utf-8')
    
    # Make the blob public
    blob.make_public()
    
    # Return the public URL
    return blob.public_url


def upload_text_public_flexible(blob_path: str, text: str) -> str:
    """
    Upload text content using local storage or GCS based on settings.
    
    Args:
        blob_path: Path for the file/blob
        text: Text content to upload
        
    Returns:
        URL or file path of the uploaded content
    """
    if settings.use_local_storage:
        # Use local storage
        full_path = os.path.join(settings.local_storage_path, blob_path)
        return upload_text_local(full_path, text)
    else:
        # Use GCS
        if not settings.gcs_bucket:
            raise ValueError("GCS bucket not configured")
        return upload_text_public(settings.gcs_bucket, blob_path, text)
