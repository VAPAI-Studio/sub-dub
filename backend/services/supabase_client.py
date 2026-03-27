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
