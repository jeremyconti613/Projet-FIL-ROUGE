from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    url = SUPABASE_URL
    key = SUPABASE_KEY

    # Si les variables d'environnement ne sont pas définies, demander à l'utilisateur.
    if not url:
        try:
            url = input("Entrez SUPABASE_URL (sera masqué dans l'historique terminal si souhaité): ").strip()
        except Exception:
            url = None
    if not key:
        try:
            key = input("Entrez SUPABASE_KEY (collez la clé, elle ne sera pas transmise via ce chat): ").strip()
        except Exception:
            key = None

    if not url or not key:
        print("Erreur: SUPABASE_URL et SUPABASE_KEY requis. Utilisez les variables d'environnement ou fournissez-les au prompt.")
        return

    supabase = create_client(url, key)

    try:
        resp = supabase.table("PlayerState").select("*").limit(10).execute()
    except Exception as e:
        print(f"Erreur lors de la requête Supabase: {e}")
        return

    # supabase-py v1 peut renvoyer un objet avec 'data' ou la liste directement
    rows = None
    if hasattr(resp, 'data'):
        rows = resp.data
    elif isinstance(resp, dict) and 'data' in resp:
        rows = resp['data']
    else:
        rows = resp

    if not rows:
        print("Aucune ligne retournée.")
        return

    print("--- 10 premières lignes de PlayerState ---")
    for i, row in enumerate(rows, start=1):
        print(f"{i}: {row}")


if __name__ == '__main__':
    main()
