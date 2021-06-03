class Behaviour:
    def __init__(self, unit):
        self.game = unit.game
        self.unit = unit

        self.complete_init()

    def complete_init(self):
        pass

    def process(self, dt):
        pass
