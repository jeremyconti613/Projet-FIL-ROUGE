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


def fetch_playerstates(run_id: int) -> pd.DataFrame:
    """Récupère les PlayerState d'une run précise, triés par Frame croissant."""
    client = get_client()
    response = (
        client.table("PlayerState")
        .select("*")
        .eq("id_run", run_id)
        .order("Frame")
        .execute()
    )
    return pd.DataFrame(response.data)


def fetch_stages(run_id: int) -> pd.DataFrame:
    """Récupère les étages (Stage) d'une run précise, triés par StageNumber croissant."""
    client = get_client()
    response = (
        client.table("Stage")
        .select("*")
        .eq("id_run", run_id)
        .order("StageNumber")
        .execute()
    )
    return pd.DataFrame(response.data)


def fetch_rooms(run_id: int) -> pd.DataFrame:
    """Récupère les rooms (Room) d'une run précise, triées par ordre d'entrée (EnterFrame)."""
    client = get_client()
    response = (
        client.table("Room")
        .select("*")
        .eq("id_run", run_id)
        .order("EnterFrame")
        .execute()
    )
    return pd.DataFrame(response.data)
