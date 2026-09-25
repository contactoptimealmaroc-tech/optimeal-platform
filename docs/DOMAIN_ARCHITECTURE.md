# OptiMeal — architecture domaine finale

## Domaine maître
- `https://optimeal.ma` — site vitrine public / Digital HQ
- `https://www.optimeal.ma` — alias du domaine maître

## Sous-domaines
- `https://carte.optimeal.ma` — carte digitale / commande. Hébergé temporairement par la plateforme de commande externe.
- `https://app.optimeal.ma` — espace applicatif protégé : Client + OptiMeal OS.
- `https://api.optimeal.ma` — API Python/FastAPI, aucune interface publique.
- `https://admin.optimeal.ma` — réservé à une phase ultérieure si nécessaire.

## Flux
Navigateur → HTTPS → reverse proxy → FastAPI → PostgreSQL.

La base PostgreSQL n'est jamais exposée à Internet.
Le navigateur peut inspecter le HTML/CSS/JS livré. Il ne reçoit pas le code Python, les secrets, la base, ni les règles métier confidentielles.

Depuis V27, cette frontière entre les 3 domaines n'est plus seulement documentée ici : elle est appliquée dans le code par `app/core/host_guard.py`, à partir des URLs déjà définies dans `.env` (`PUBLIC_BASE_URL`, `APP_BASE_URL`, `API_BASE_URL`). Tant que ces 3 valeurs sont identiques (développement local), le garde-fou reste inactif.

## DNS à créer
- A `@` → IP serveur
- CNAME `www` → `optimeal.ma`
- A/CNAME `app` → serveur applicatif
- A/CNAME `api` → serveur API
- `carte` → cible fournie par la plateforme de commande externe

## Déploiement
1. DNS.
2. TLS/HTTPS pour chaque hostname.
3. Reverse proxy.
4. Conteneur FastAPI.
5. PostgreSQL privé.
6. Variables secrètes côté serveur.
7. Tests de santé et sauvegardes.
