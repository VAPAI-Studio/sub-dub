import os
from supabase import create_client, Client

_supabase_client = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client singleton
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")

        _supabase_client = create_client(url, key)

    return _supabase_client


# ===== Storage Helpers =====

def upload_file(bucket, path, file_bytes, content_type="audio/mpeg"):
    """Upload a file to Supabase Storage. Overwrites if exists."""
    client = get_supabase_client()
    # Remove existing file first (upsert)
    try:
        client.storage.from_(bucket).remove([path])
    except Exception:
        pass
    client.storage.from_(bucket).upload(path, file_bytes, {"content-type": content_type})


def download_file(bucket, path):
    """Download a file from Supabase Storage. Returns bytes."""
    client = get_supabase_client()
    return client.storage.from_(bucket).download(path)


def delete_file(bucket, path):
    """Delete a file from Supabase Storage."""
    client = get_supabase_client()
    try:
        client.storage.from_(bucket).remove([path])
    except Exception:
        pass


def get_public_url(bucket, path):
    """Get public URL for a file in Supabase Storage."""
    client = get_supabase_client()
    return client.storage.from_(bucket).get_public_url(path)
