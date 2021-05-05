class UnitManager:
    def __init__(self, game):
        self.game = game

        self.units = []

    def add_unit(self, unit):
        self.units.append(unit)

    def update(self):
        for unit in self.units:
            unit.update()

    def render(self, surf, offset=(0, 0)):
        for unit in self.units:
            unit.render(surf, shift=offset)
