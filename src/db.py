import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Please set DATABASE_URL environment variable (Postgres connection string)")


def get_engine() -> Engine:
    """Return a SQLAlchemy Engine using `DATABASE_URL`."""
    # echo=False to avoid verbose SQL logging; adjust as needed
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def fetch_all(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a query and return all rows as list of dicts."""
    engine = get_engine()
    with engine.connect() as conn:
        result: Result = conn.execute(text(query), params or {})
        rows = [dict(row._mapping) for row in result]
    return rows


def execute(query: str, params: Optional[Dict[str, Any]] = None) -> None:
    """Execute a statement (INSERT/UPDATE/DELETE)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(query), params or {})


def test_connection() -> bool:
    """Simple test: select version() from Postgres."""
    try:
        rows = fetch_all("SELECT version() as v;")
        return bool(rows)
    except Exception:
        return False
