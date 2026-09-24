# OptiMeal Platform V27

Structure cible :

- `optimeal.ma` / `www.optimeal.ma` → vitrine publique
- `carte.optimeal.ma` → carte digitale / commande externe (temporaire)
- `app.optimeal.ma` → application Client + OptiMeal OS
- `api.optimeal.ma` → backend Python FastAPI
- PostgreSQL → privé, jamais exposé

Nouveau en V27 : le code est découpé en modules Python étanches (`app/site`, `app/auth`, `app/client_app`, `app/admin_app`, `app/core`) et deux garde-fous serveur ont été ajoutés — voir `docs/ARCHITECTURE.md`.

## Lancer en local

1. Copier `.env.example` vers `.env`.
2. Définir `SECRET_KEY`.
3. Créer un environnement virtuel et installer les dépendances :
   ```
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Lancer le serveur :
   ```
   uvicorn app.main:app --reload
   ```
5. Créer un premier utilisateur (le script initialise aussi les tables) :
   ```
   python -c "from app.core.db import Base, engine; import app.core.models; Base.metadata.create_all(bind=engine)"
   python scripts/create_user.py --email admin@optimeal.ma --password CHANGE_ME --role ADMIN --name Admin
   ```
6. Ouvrir `http://127.0.0.1:8000/` (vitrine), `http://127.0.0.1:8000/connexion` (connexion).
7. Tester `http://127.0.0.1:8000/api/v1/health`.

## Lancer avec Docker (staging / production)

1. Copier `.env.example` vers `.env` et renseigner `SECRET_KEY` et `POSTGRES_PASSWORD`.
2. `docker compose up --build`.
3. Le reverse proxy nginx (`deploy/nginx/optimeal.conf`) route déjà `optimeal.ma`, `app.optimeal.ma` et `api.optimeal.ma` vers le même conteneur ; c'est `core/host_guard.py` qui empêche chaque domaine de répondre en dehors de son périmètre dès que `PUBLIC_BASE_URL`/`APP_BASE_URL`/`API_BASE_URL` sont distincts dans `.env`.
4. Mettre HTTPS devant nginx (Certbot/Caddy) avant d'exposer publiquement.

## Tests

```
pytest tests/
```

## Sécurité

- HTTPS à mettre devant Nginx en production.
- Cookie de session HttpOnly/SameSite.
- CORS limité aux domaines OptiMeal.
- API et pages HTML protégées par vérification serveur (pas seulement côté client) — voir `core/page_guard.py`.
- Frontière de domaines imposée en code — voir `core/host_guard.py`.
- PostgreSQL non publié en port hôte.
- Ne jamais placer secrets, règles de matching propriétaires, données clients ou credentials fournisseurs dans le frontend.

## Suite de construction

- Alembic + migrations versionnées.
- Audit log.
- CSRF adapté au mode cookie.
- Rate limiting / anti-bruteforce.
- Modèle Client/ON1/ON2/Cycle/Menu/Matching/Stock/Fournisseurs conforme au CDC/OS/SOP validé.
- Tests end-to-end Client → Matching → Menu verrouillé → Supply.
