import dataclasses
from typing import Dict, List

import snecs

from nqp.core.data import Data
from nqp.core.effect import load_effect


@dataclasses.dataclass
class ItemData:
    """
    Schema for the YAML Item data files

    """

    name: str
    is_signature: bool
    effects: List[Dict[str, str]]


class Item(snecs.RegisteredComponent):
    """
    Item component -- WIP

    """

    def __init__(self, name, is_signature, effects):
        self.name: str = name
        self.is_signature = is_signature
        self.effects = effects


def create_item(data: Data, name: str):
    """
    Return new Item instance by name

    Args:
        data: Game Data object
        name: Short name of the item, same as the filename without extension

    Returns:
        New Item instance

    """
    item_data = data.items[name]
    return Item(
        name=item_data.name,
        is_signature=item_data.is_signature,
        effects=[load_effect(data) for data in item_data.effects],
    )
