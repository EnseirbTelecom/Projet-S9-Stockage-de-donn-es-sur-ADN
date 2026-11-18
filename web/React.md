# Guide de manipulation du frontend (`web/`)

Document à destination des collaborateurs qui veulent faire évoluer la page
de démonstration. Il décrit l'architecture actuelle du frontend, le contrat
de données entre l'API et la page, et donne des recettes concrètes de
manipulation — notamment pour faire évoluer la page d'une simple
démonstration technique vers une **page académique de démo personnalisée**,
avec une présentation plus « produit ».

---

## 1. Architecture actuelle

```text
web/
  index.html               Titre de l'onglet, point d'entrée HTML
  vite.config.js           Proxy /api -> API (development), port 3000
  src/
    main.jsx               Point d'entrée, importe styles.css
    App.jsx                Page principale : machine à états de la démo
    styles.css             Design system complet (variables + classes)
    lib/
      api.js               Appels vers l'API (runTransmission)
    components/
      ControlPanel.jsx     Saisie du message, taux d'erreur, options
      Pipeline.jsx         Nœuds d'étapes cliquables (chaîne de transmission)
      StepDetail.jsx       Vue détaillée d'une étape (entrée / sortie)
      DataViews.jsx        Rendu des données : texte, bits, séquence ADN
      SummaryPanel.jsx     Bilan final (intégrité, statistiques, graine)
```

### Flux de données

Le frontend est une **coquille d'affichage** : toute la logique de la chaîne
de transmission vit dans l'API.

```text
ControlPanel (état des contrôles)
   |  runTransmission() — lib/api.js
   v
POST /api/communication/run
   |  réponse JSON : steps[], stats, integrity, seed
   v
App.jsx : machine à états
   |  result, currentStep, playing
   v
Pipeline -> StepDetail -> SummaryPanel
```

- `App.jsx` reçoit la réponse complète en une seule requête, puis **anime**
  `currentStep` (minuteur `STEP_DURATION`, 1500 ms par étape) ou navigue
  manuellement (clic sur un nœud, boutons étape précédente / suivante).
- Le pipeline est **piloté par les données** : il dessine autant de nœuds que
  d'étapes renvoyées par l'API, dans l'ordre de `steps[]`. Ajouter une étape
  côté backend ne demande donc *aucune* modification de `Pipeline.jsx`.
- `SummaryPanel` n'apparaît qu'à la dernière étape (`isComplete`).

### Machine à états d'`App.jsx`

| État | Rôle |
|---|---|
| `result` | Réponse complète du dernier `POST /communication/run` ; `null` tant qu'aucune transmission n'a été lancée |
| `currentStep` | Index de l'étape affichée (0 à `steps.length - 1`) |
| `playing` | Animation automatique en cours (avance d'une étape toutes les 1500 ms) |
| `loading` | Requête en cours (désactive le bouton) |
| `error` | Message d'erreur affiché dans la bannière rouge |

`useEffect` dans `App.jsx` pilote l'avancement : si `playing` et pas encore
à la dernière étape, un `setTimeout` incrémente `currentStep` ; l'animation
s'arrête d'elle-même à la fin.

### Contrat de réponse de `/communication/run`

Chaque élément de `steps[]` contient :

| Champ | Contenu |
|---|---|
| `id` | Identifiant stable (`source`, `bits`, `encode`, `protect`, `channel`, `restore`, `decode`, `result`) |
| `label`, `description` | Texte affiché dans le nœud du pipeline et le détail d'étape |
| `kind` | Type dominant de l'étape : `text`, `bits` ou `dna` |
| `input_kind` / `output_kind` | Type des données d'entrée et de sortie (ils peuvent différer, ex. conversion binaire) |
| `input` / `output` | Les données brutes des deux côtés |
| `strategy` | Nom de l'implémentation utilisée (badge) |
| `errors` | `channel` uniquement : substitutions introduites (`index`, `original`, `received`) |
| `corrections` | `restore` uniquement : bases corrigées (`block`, `index`, `received`, `corrected`) |
| `error_rate` | `channel` uniquement |

Plus, au niveau racine : `original_message`, `received_message`, `integrity`,
`seed`, `stats` (bits, bases, erreurs injectées / corrigées, protection).

Les types `kind` déterminent le rendu dans `DataViews.jsx` :
`text` -> `TextBlock`, `bits` -> `BitsBlock` (groupes de 8), `dna` ->
`DnaBlock` (tuiles colorées par base, avec surlignage des erreurs /
corrections via `markedIndices`).

---

## 2. Design system (`styles.css`)

Toute l'apparence passe par les variables de `:root` :

| Variable | Usage | Valeur actuelle |
|---|---|---|
| `--color-primary` | Titres, accents profonds | Bleu nuit `#16324f` |
| `--color-accent` | Boutons, nœud actif, liens | Bleu `#2f6fed` |
| `--color-bg` | Fond de page | `#f4f6f9` |
| `--base-a/t/c/g` | Couleurs des bases ADN | Vert / rouge / bleu / ocre |
| `--color-error*`, `--color-ok*` | Badges et surlignages | Rouge / vert |

Une carte = classe `.card`. L'en-tête de page utilise un dégradé défini dans
`.site-header`. La grille passe en une seule colonne sous 820 px
(bloc `@media` en fin de fichier).

Règle : **ne jamais** coder une couleur en dur dans un composant — passer
par une variable `:root`.

---

## 3. Recettes de manipulation

### 3.1 Rendre la page « à nous » (identité et ton)

1. **Titres et sous-titres** : `site-header h1`/`p` dans `App.jsx`,
   `<title>` dans `index.html`, en-têtes de `ControlPanel.jsx`.
2. **Palette** : ajuster `:root` dans `styles.css` (une seule ligne par
   couleur, la page entière suit).
3. **Textes pédagogiques** : `intro-list` (carte « Comment fonctionne la
   démonstration ») et `architecture-card` (constante `ARCHITECTURE` dans
   `App.jsx`) — à réécrire avec les références du cours et les noms de vos
   implémentations réelles.
4. **Exemples de messages** : `SAMPLE_MESSAGES` dans `ControlPanel.jsx`.

### 3.2 Orientation « produit » de la démo

Le jury attend une démo plus produit : la page est déjà construite pour cela,
car le contenu affiché **vient de l'API** et non du code. Pistes, par ordre
de rendement :

1. **Sélection des stratégies alimentée par le catalogue (implémenté)** :
   l'endpoint `GET /api/catalog` renvoie le petit JSON de description de
   chaque implémentation (`slug`, `name`, `description`, `parameters`),
   enregistrées dans le registre `app/catalog.py` côté API.
   `ControlPanel.jsx` construit un sélecteur par catégorie (encodeur,
   décodeur, canal, protection) à partir de ce catalogue : ajouter une
   implémentation côté backend la rend visible dans le site sans toucher
   au frontend. Les étapes renvoyées par `/communication/run` portent
   elles-mêmes `strategy` et `description` issus des métadonnées.
2. **Mesures comparatives « produit »** : la carte de bilan (`SummaryPanel`)
   est l'endroit idéal pour un taux de correction, un débit de bases par
   octet d'origine, ou une comparaison protection activée / désactivée selon
   le taux d'erreur. Ajouter les champs dans `stats` (API) puis les afficher.
3. **Mode reproductibilité** : la graine est déjà retournée dans la réponse.
   Pour une démo produit, permettre de repartir d'une graine affichée
   (le champ de saisie existe déjà dans `ControlPanel.jsx`).
4. **Narration** : ancres de page ou un bandeau d'avancement par grandes
   phases (émission / canal / réception) en regroupant les étapes par `id`.
5. **Écrans** : la grille `.step-data-grid` permet d'ajouter un panneau
   (ex. codec binaire affiché à la fois en bits et en octets) sans casser la
   mise en page (penser à ajuster `grid-template-columns`).

### 3.3 Ajouter une étape au pipeline

C'est une modification **backend d'abord** (voir checklist du `README.md`,
section 5). Côté frontend :

1. Le nœud apparaît automatiquement dans `Pipeline.jsx` (rendu générique).
2. Si l'étape produit un type de données nouveau, enrichir `DataViews.jsx` :
   un bloc de rendu + une entrée dans `KIND_LABELS` (`StepDetail.jsx`) +
   éventuellement une entrée dans `DataLegend`.
3. Si l'étape porte des événements à surligner (comme `errors` du canal),
   ajouter une branche dans `StepDetail.jsx` sur le `id` de l'étape, avec le
   tableau correspondant (composant `ErrorTable`).

Ne jamais reconstruire la logique côté client : tout ce que `StepDetail`
affiche doit venir de l'étape reçue.

### 3.4 Ajouter un contrôle utilisateur

1. Ajouter le champ (état local) dans `ControlPanel.jsx`.
2. L'ajouter au corps de la requête dans `runTransmission` (`lib/api.js`),
   en respectant le nom de champ attendu par `TransmissionRequest` dans
   `routers/communication.py`.
3. Côté backend : ajouter le champ à `TransmissionRequest` avec une
   validation (`Field`), puis le consommer dans la chaîne.
4. Vérifier le traitement des erreurs déjà en place : `api.js` remonte le
   `detail` de la réponse d'erreur dans la bannière rouge.

### 3.5 Régler l'animation

- **Vitesse globale** : `STEP_DURATION` dans `App.jsx` (ms par étape).
- **Pulsation du nœud actif** : animation `@keyframes pulse` dans
  `styles.css`.
- **Relation vitesse / lecture** : les boutons de navigation mettent
  automatiquement l'animation en pause (`goTo`) ; conserver ce comportement.

### 3.6 Changer la mise en page

- En-tête pleine largeur : `.site-header`.
- Contenu largeur maximale 1180 px : `.content`.
- Ajouter une section statique (ex. présentation de l'équipe) : une
  `<section class="card">` dans `App.jsx` et, si besoin, un style dédié dans
  `styles.css` — suivre la même convention de commentaire par bloc.

---

## 4. Conventions à respecter

1. **Pas de logique métier dans le frontend.** Encodeurs, canaux,
   corrections : tout est exécuté par l'API. Le frontend ne transforme
   jamais les données, il les affiche et les met en évidence.
2. **Composants indépendants de l'implémentation.** Les noms de stratégies
   (`one2one`, `replication-x3`, `substitution`) sont des libellés reçus de
   l'API, pas des branchements de code : ne pas graver l'identité d'une
   implémentation dans le rendu.
3. **Patchs de style via variables** (`:root`), jamais en dur dans les
   classes des composants.
4. **Pas de dépendance npm supplémentaire** sans discussion : chaque
   dépendance allonge le build CI (`web-build`) et la containerisation.
5. **Vérifier avant de pousser** :

   ```bash
   cd web
   npm install
   npm run build
   ```

   Le job CI `web-build` exécute exactement ces commandes.
6. **Rester responsive** : toute nouvelle grille ajoutée doit avoir son
   équivalent dans le bloc `@media (max-width: 820px)`.

---

## 5. Démarrage rapide pour développer

Avec l'API locale (hors Docker) :

```bash
# Terminal 1 : API
cd api
uvicorn app.main:app --port 8000 --reload

# Terminal 2 : frontend avec proxy vers localhost:8000
cd web
npm install
npm run dev        # http://localhost:3000
```

Avec Docker : `docker compose up -d` puis http://localhost:3000 (le proxy
utilise alors `http://api:8000` via `API_PROXY_TARGET` dans docker-compose).
