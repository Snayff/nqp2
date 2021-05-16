from scripts.scenes.combat.elements.unit_behaviors.behavior import Behavior


class Swarm(Behavior):
    def complete_init(self):
        # these are pointers. be careful with modifying them.
        self.target = None
        self.target_pos = None

    def find_target(self):
        """
        Find the nearest enemy from a different team and update the target.
        """
        nearest = [None, 9999999]
        for entity in self.game.combat.all_entities:
            if entity.team != self.unit.team:
                dis = entity.dis(self.unit)
                if dis < nearest[1]:
                    nearest = [entity, dis]

        self.target = nearest[0]
        if nearest[0]:
            self.target_pos = self.target.pos
        else:
            self.target_pos = None

    def process(self, dt):
        if (not self.target) or (not self.target.alive):
            self.find_target()
