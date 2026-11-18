# Intégration continue (CI)

Ce document décrit le fonctionnement de la CI GitHub du projet et la marche à
suivre pour les collaborateurs. Il complète la section 6 du `README.md`.

## 1. Vue d'ensemble

La CI est définie par le fichier [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
Elle s'exécute automatiquement :

- à chaque **push** sur les branches `main` et `master` ;
- sur **chaque Pull Request**, quelle que soit la branche source.

| Job | Environnement | Répertoire | Commande vérifiée |
|---|---|---|---|
| `api-tests` | Python 3.12, `ubuntu-latest` | `api/` | `pytest -v` |
| `web-build` | Node 22, `ubuntu-latest` | `web/` | `npm run build` |

Le job `api-tests` installe `requirements.txt` (dépendances de production,
versions épinglées) **et** `requirements-dev.txt` (pytest, httpx), puis exécute
toute la suite de tests. Le job `web-build` vérifie que le frontend compile
sans erreur avec Vite ; il n'exécute pas l'application.

## 2. Ce que la CI garantit

- Toute implémentation d'élément de la chaîne (encodeur, décodeur, canal,
  protection) respecte la **classe abstraite** de sa catégorie et fonctionne
  à travers son **wrapper** (les tests appellent systématiquement les wrappers).
- Les **endpoints** de test et d'orchestration répondent conformément aux
  contrats établis (codes HTTP, structure JSON, ordre des étapes).
- La chaîne complète reste fonctionnelle : aucun test de régression ne peut
  passer au rouge suite à l'ajout d'un nouvel élément.
- Le site de démonstration reste compilable.

## 3. Avant de pousser : reproduire la CI en local

Exécutez les mêmes commandes que la CI pour éviter les allers-retours :

```bash
# API (depuis la racine du projet)
cd api
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest

# Frontend (depuis la racine du projet)
cd web
npm install
npm run build
```

Si les deux commandes passent en local, les jobs CI passeront.

Remarque : sur une machine locale en Python >= 3.13, `psycopg2-binary==2.9.9`
peut échouer à se compiler ; cette situation ne se produit pas en CI
(Python 3.12). Voir la section 6.

## 4. Suivre les résultats sur GitHub

1. Ouvrir l'onglet **Actions** du dépôt : chaque push et chaque PR y apparaît.
2. Sur une Pull Request, la zone **Checks** affiche les deux jobs
   (`Tests API (pytest)` et `Build frontend (Vite)`).
3. En cas d'échec, ouvrir le job concerné pour consulter la sortie pytest
   ou le message d'erreur de build.
4. Cliquer sur « Re-run all jobs » relance l'exécution sans pousser de commit.

## 5. Règles pour les collaborateurs

- **Une Pull Request ne doit être fusionnée que si les deux jobs sont verts.**
- Exécuter `pytest` **avant** de pousser (section 3).
- Tout nouvel élément de la chaîne doit être couvert par des tests :
  voir la checklist « Ajouter un élément de transmission » dans le
  `README.md` (section 5).
- Une PR ne doit pas modifier `requirements.txt` sans justifier dans sa
  description le changement de version.
- En cas d'échec CI non lié à votre modification (infrastructure GitHub),
  prévenir l'équipe et relancer le job avant d'investiguer.

## 6. Erreurs fréquentes et résolutions

| Symptôme | Cause probable | Solution |
|---|---|---|
| `FAILED ... ImportError: No module named 'app'` | pytest lancé hors de `api/` | Exécuter `pytest` depuis le répertoire `api/` (le `conftest.py` racine gère les imports) |
| `error: failed-wheel-build-for-install` sur `psycopg2-binary` en local | Python local >= 3.13 sans wheel précompilé | Utiliser Python 3.12 (comme la CI) ou monter la version de `psycopg2-binary` |
| Test d'API `500 Internal Server Error` sur un endpoint d'implémentation | Nouvelle implémentation non enregistrée dans le mécanisme de sélection de `routers/tests.py` | Ajouter la classe dans le bloc de sélection et ses imports |
| `assert 400 == 200` sur `/tests/...` | Entrée invalide dans le test : toutes les entrées DOMAINE valides doivent être acceptées | Vérifier la validation et le type des paramètres |
| `npm run build` échoue avec une erreur de syntaxe JSX | Composant frontend cassé | Corriger localement (message de Vite : fichier et ligne) |
| Le job CI échoue alors que tout passe en local | Divergence d'environnement (versions, cache) | Vérifier `requirements.txt` épinglés, supprimer le cache Actions si suspect |

## 7. Faire évoluer la CI

Pour ajouter un job (lint Python, tests de charge, constructions Docker,
déploiement), modifier `.github/workflows/ci.yml` en suivant la structure
existante (un job = un environnement isolé, `working-directory` fixé).
Toute modification du workflow doit être validée par une Pull Request,
elle-même soumise à la CI.

Versions actuellement utilisées : Python 3.12 (`actions/setup-python@v5`),
Node 22 (`actions/setup-node@v4`), `actions/checkout@v4`. Pressé de monter
de version : modifier le champ `python-version` ou `node-version` et laisser
la CI valider la compatibilité.
