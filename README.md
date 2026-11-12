# Projet-S9-Stockage-de-donn-es-sur-ADN

# Développement de la chaîne de communication

## 1. Architecture générale

Chaque nouvel élément de la chaîne de communication (encodeur, décodeur, canal de transmission, mécanisme de correction d'erreurs, etc.) doit respecter une architecture commune reposant sur trois éléments :

1. **Une classe abstraite**, placée dans `core/`, qui définit le comportement attendu de l'élément.
2. **Un wrapper**, placé dans `wrappers/`, qui fournit une interface commune permettant d'utiliser les différentes implémentations.
3. **Une implémentation concrète**, placée dans le dossier correspondant à la catégorie de l'élément (`encoders/`, `decoders/`, `channels/`, etc.).

Chaque nouvel élément doit également être accessible depuis l'API pour pouvoir être testé individuellement et intégré à la chaîne complète.

## 2. Étapes d'implémentation

### Étape 1 : Créer la classe abstraite dans `core/`

La classe abstraite définit le contrat que toutes les implémentations d'une même catégorie doivent respecter.

Elle doit :
- Hériter de `ABC`.
- Définir les méthodes communes à toutes les implémentations à l'aide de `@abstractmethod`.
- Définir les paramètres et les types de retour attendus.

Exemple de structure :

```python
from abc import ABC, abstractmethod

class BaseElement(ABC):

    @abstractmethod
    def process(self, data):
        pass
```

Le nom de la classe et celui des méthodes doivent être adaptés à la catégorie concernée.

### Étape 2 : Créer le wrapper dans `wrappers/`

Le wrapper permet de manipuler les différentes implémentations à travers une interface commune.

Il doit :
- Recevoir une instance d'une implémentation concrète.
- Vérifier ou garantir la compatibilité avec la classe abstraite correspondante.
- Exposer les méthodes permettant d'utiliser l'élément.
- Centraliser, si nécessaire, les opérations communes aux différentes implémentations.

Exemple de structure :

```python
class Element:

    def __init__(self, strategy):
        self.strategy = strategy

    def process(self, data):
        return self.strategy.process(data)
```

Le wrapper ne doit pas contenir la logique métier propre à une implémentation particulière.

### Étape 3 : Créer l'implémentation dans le dossier correspondant

L'implémentation concrète doit être placée dans le dossier dédié à sa catégorie.

Exemples :
- `encoders/` : algorithmes d'encodage.
- `decoders/` : algorithmes de décodage.
- `channels/` : modèles de canaux de transmission.
- Autres dossiers selon les besoins de la chaîne.

Chaque implémentation doit :
- Hériter de la classe abstraite correspondante.
- Implémenter toutes les méthodes abstraites.
- Contenir uniquement la logique métier qui lui est propre.
- Respecter les entrées et sorties définies par la classe abstraite.

Exemple :

```python
from app.core.base_element import BaseElement

class MyElement(BaseElement):

    def process(self, data):
        # Implémentation de l'algorithme
        return data
```

### Étape 4 : Ajouter un endpoint de test dans `routers/tests.py`

Chaque nouvelle implémentation doit disposer d'un endpoint permettant de la tester indépendamment du reste de la chaîne.

Dans `tests.py`, il faut :
1. Importer la nouvelle implémentation.
2. Importer le wrapper correspondant.
3. Ajouter l'implémentation dans le mécanisme de sélection des algorithmes.
4. Appeler le wrapper pour exécuter le traitement.
5. Retourner le résultat au format JSON.
6. Gérer les erreurs avec des exceptions HTTP adaptées.

L'objectif est de pouvoir vérifier le fonctionnement de chaque composant indépendamment des autres.

Les endpoints de test doivent rester regroupés dans le router dédié aux tests.

### Étape 5 : Mettre à jour l'endpoint de communication globale

Si le nouvel élément intervient dans la chaîne de communication complète, il faut également mettre à jour l'endpoint correspondant dans `routers/communication.py`.

Il faut notamment :
- Importer le wrapper et l'implémentation nécessaires.
- Ajouter l'élément à l'étape appropriée de la chaîne.
- Respecter l'ordre d'exécution des différents traitements.
- Assurer la compatibilité entre les données produites par l'étape précédente et celles attendues par la suivante.
- Adapter les paramètres de configuration de la chaîne si nécessaire.

L'endpoint global doit orchestrer les différents composants sans reproduire leur logique métier.

## 3. Vérifications avant de proposer une Pull Request

Avant de soumettre une modification, vérifier les points suivants :

- [ ] La classe abstraite est présente dans `core/` si une nouvelle catégorie d'élément est créée.
- [ ] Le wrapper est présent dans `wrappers/`.
- [ ] L'implémentation concrète est présente dans le dossier correspondant.
- [ ] Toutes les méthodes abstraites sont implémentées.
- [ ] L'élément est accessible via un endpoint dans `routers/tests.py`.
- [ ] Les entrées et sorties sont correctement validées.
- [ ] Les erreurs sont correctement gérées.
- [ ] L'endpoint global de communication est mis à jour si nécessaire.
- [ ] Les tests individuels et les tests de la chaîne complète sont fonctionnels.
- [ ] La documentation est mise à jour si de nouveaux paramètres ou comportements sont introduits.

## 4. Principes d'architecture à respecter

Quelques règles doivent être conservées tout au long du développement :

- **Séparation des responsabilités :** la logique métier appartient aux implémentations concrètes, pas aux wrappers ni aux endpoints.
- **Modularité :** chaque élément doit pouvoir être développé et testé indépendamment.
- **Extensibilité :** ajouter un nouvel algorithme ne doit pas nécessiter de modifier les implémentations existantes.
- **Réutilisabilité :** les wrappers doivent permettre de manipuler différentes implémentations de manière homogène.
- **Cohérence :** toutes les implémentations d'une même catégorie doivent respecter le contrat défini par leur classe abstraite.

L'objectif est de construire une chaîne de communication modulaire, évolutive et facilement maintenable