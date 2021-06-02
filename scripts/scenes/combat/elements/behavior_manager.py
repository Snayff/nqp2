import os


class BehaviourManager:
    def __init__(self):
        self.unit_behaviours = {}
        self.entity_behaviours = {}

        # load unit behaviours
        for behaviour in os.listdir("scripts/scenes/combat/elements/unit_behaviours"):
            if behaviour not in ["__pycache__"]:
                # chop off the .py
                behaviour = behaviour.split(".")[0]

                # only works with single-word class names for now
                class_name = behaviour[0].upper() + behaviour[1:]
                module = __import__("scripts.scenes.combat.elements.unit_behaviours." + behaviour, fromlist=[class_name])
                self.unit_behaviours[behaviour] = getattr(module, class_name)

        # load entity behaviours
        for behaviour in os.listdir("scripts/scenes/combat/elements/entity_behaviours"):
            if behaviour not in ["__pycache__"]:
                # chop off the .py
                behaviour = behaviour.split(".")[0]

                # only works with single-word class names for now
                class_name = behaviour[0].upper() + behaviour[1:]
                module = __import__(
                    "scripts.scenes.combat.elements.entity_behaviours." + behaviour, fromlist=[class_name]
                )
                self.entity_behaviours[behaviour] = getattr(module, class_name)
