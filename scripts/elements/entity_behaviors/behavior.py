class Behavior:
    def __init__(self, entity):
        self.game = entity.game
        self.entity = entity

        self.complete_init()

    def complete_init(self):
        pass

    def process(self, dt):
        pass
