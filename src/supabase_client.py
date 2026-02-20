import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_table(table: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Return rows from a Supabase table."""
    res = supabase.table(table).select("*").limit(limit).execute()
    data = getattr(res, "data", None) or res.get("data")
    error = getattr(res, "error", None) or res.get("error")
    if error:
        raise RuntimeError(f"Supabase error: {error}")
    return data or []


def insert_row(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a row into a Supabase table and return the inserted row(s)."""
    res = supabase.table(table).insert(row).execute()
    data = getattr(res, "data", None) or res.get("data")
    error = getattr(res, "error", None) or res.get("error")
    if error:
        raise RuntimeError(f"Supabase error: {error}")
    return data
