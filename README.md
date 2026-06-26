# Projet-FIL-ROUGE

## Setup

Ce projet utilise [uv](https://docs.astral.sh/uv/) pour la gestion des dépendances.

```bash
# Installer les dépendances et créer l'environnement virtuel
uv sync

# Lancer l'application Streamlit
uv run streamlit run streamlit_app.py

# Ajouter une dépendance
uv add <package>
```

> **Note :** `requirements.txt` est généré automatiquement via `uv export` — ne pas le modifier
> directement. Éditer `pyproject.toml` puis relancer `uv lock && uv export --no-hashes --no-dev --no-emit-project -o requirements.txt`.