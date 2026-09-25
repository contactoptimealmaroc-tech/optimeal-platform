# OptiMeal Secure V27

## Boundary de sécurité

Le navigateur est considéré comme **non fiable**. Tout ce qui est livré au navigateur est inspectable — c'est une propriété du web, pas un bug : "Afficher le code source" fonctionnera toujours. La séparation ne consiste donc pas à "cacher" du HTML, mais à garantir que ce qui est livré au navigateur ne contient jamais de secret, de règle métier propriétaire, ni de donnée d'un autre utilisateur, et que l'accès y est vérifié côté serveur.

## Séparation en modules Python (nouveau en V27)

```
app/
  core/        config, DB, sécurité (JWT/mots de passe), garde-fous — partagé, sans logique métier
  site/        vitrine publique — ne dépend d'aucun autre module
  auth/        connexion / session — pont entre vitrine et espaces protégés
  client_app/  API + page + template de l'espace CLIENT
  admin_app/   API + page + template + moteur de menu de l'espace ADMIN/CHEF/NUTRITION (OS)
```

Chaque domaine possède ses propres schémas Pydantic, son propre template HTML et ses propres routes. `site/` ne doit jamais importer `client_app/` ou `admin_app/`, et inversement.

### Public
`frontend/public/index.html` contient uniquement les pages publiques : accueil, carte, formules, approche, fonctionnement, qui sommes-nous, contact.

### Privé
- `/connexion` : formulaire de connexion (module `auth`).
- `/client` : application Client (module `client_app`), page servie uniquement si la session est valide et le rôle est CLIENT.
- `/os` : application OS/Admin (module `admin_app`), page servie uniquement si la session est valide et le rôle est ADMIN/CHEF/NUTRITION.
- `/api/v1/client/*` : API Client protégée par rôle CLIENT.
- `/api/v1/os/*` : API OS protégée par rôles ADMIN/CHEF/NUTRITION.

### Deux garde-fous serveur (nouveau en V27)
1. **`core/page_guard.py`** — avant V27, `/client` et `/os` renvoyaient leur HTML à n'importe qui ; seul le JavaScript découvrait après coup (401 de l'API) qu'il fallait rediriger. Désormais, la vérification de session/rôle se fait **avant** d'envoyer le moindre octet de HTML : redirection serveur vers `/connexion` sinon.
2. **`core/host_guard.py`** — applique en code la frontière de domaines décrite dans `DOMAIN_ARCHITECTURE.md` (vitrine / app / api), à partir des variables déjà présentes dans `.env` (`PUBLIC_BASE_URL`, `APP_BASE_URL`, `API_BASE_URL`). Inactif en local (un seul hôte en dev), actif dès que les 3 domaines sont distincts (production).

### Données sensibles
Ne jamais mettre dans le frontend : secrets, mots de passe, règles de matching propriétaires, données de tous les clients, tokens d'administration, paramètres internes, credentials fournisseurs, ou logique qui doit rester confidentielle. C'est déjà le cas : `admin_app/services.py` (moteur de menu) ne s'exécute que côté serveur.

### Prochaine migration
1. Remplacer le moteur de menu déterministe par les règles de cycle/matching/menu/stock du CDC/OS/SOP validé.
2. Ajouter migrations Alembic (actuellement `create_all` au démarrage).
3. Ajouter audit log, CSRF si authentification par cookie avec mutations cross-origin, rate limiting, validation stricte, sauvegardes PostgreSQL et monitoring.
4. Déployer derrière HTTPS + reverse proxy (voir `deploy/nginx/optimeal.conf`).
