from fastapi import APIRouter

from app.catalog import REGISTRY

router = APIRouter(
    prefix="/catalog",
    tags=["Catalogue"]
)


@router.get("")
def catalog():
    """Petit JSON de description de chaque implémentation, par catégorie.

    Consommé par le site web : les sélecteurs de stratégies, les
    descriptions affichées et les paramètres proposés proviennent de
    ce catalogue, ce qui rend la page adaptable à toute nouvelle
    implémentation enregistrée dans `app/catalog.py`.
    """
    return {
        category: [cls.describe() for cls in strategies.values()]
        for category, strategies in REGISTRY.items()
    }
