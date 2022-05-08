import dataclasses
from typing import Dict, List

import snecs


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

    def __init__(self, name: str, is_signature: bool):
        self.name: str = name
        self.is_signature: bool = is_signature
