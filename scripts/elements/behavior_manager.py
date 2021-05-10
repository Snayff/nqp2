import os

class BehaviorManager:
    def __init__(self):
        self.unit_behaviors = {}
        self.entity_behaviors = {}

        # load unit behaviors
        for behavior in os.listdir('scripts/elements/unit_behaviors'):
            if behavior not in ['__pycache__']:
                # chop off the .py
                behavior = behavior.split('.')[0]

                # only works with single-word class names for now
                class_name = behavior[0].upper() + behavior[1:]
                module = __import__('scripts.elements.unit_behaviors.' + behavior, fromlist=[class_name])
                self.unit_behaviors[behavior] = getattr(module, class_name)

        # load entity behaviors
        for behavior in os.listdir('scripts/elements/entity_behaviors'):
            if behavior not in ['__pycache__']:
                # chop off the .py
                behavior = behavior.split('.')[0]

                # only works with single-word class names for now
                class_name = behavior[0].upper() + behavior[1:]
                module = __import__('scripts.elements.entity_behaviors.' + behavior, fromlist=[class_name])
                self.entity_behaviors[behavior] = getattr(module, class_name)
