# src/db.py

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase_client: Client = None

def get_client() -> Client:
    """Instancie le client Supabase uniquement au premier appel."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def fetch_all(table: str, select: str = "*") -> pd.DataFrame:
    """Récupère toutes les lignes d'une table avec pagination automatique."""
    client    = get_client()        # ✅ utilise get_client() et non supabase
    all_data  = []
    page_size = 1000
    offset    = 0

    while True:
        response = client.table(table).select(select).range(
            offset, offset + page_size - 1
        ).execute()
        data = response.data
        if not data:
            break
        all_data.extend(data)
        if len(data) < page_size:
            break
        offset += page_size

    return pd.DataFrame(all_data)
