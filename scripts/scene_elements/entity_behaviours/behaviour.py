class Behaviour:
    # TODO - rename as EntityBehaviour
    # TODO - make ABC
    def __init__(self, entity):
        self._game = entity._game
        self.entity = entity

        self.complete_init()

    def complete_init(self):
        pass

    def process(self, dt):
        pass
