class Trap:
    def __init__(self, game, loc, type, trigger=("time", 1)):
        self._game = game
        self.type = type
        self.loc = loc
        self.trigger_type = trigger
        self.timer = 0
        self.animation_timer = 0
        self.animation_dur = 0.5
        self.is_triggered = False
        self.prox_reset_time = -1
        self.size = [16, 16]

    def trigger(self):
        self.is_triggered = True

    def update(self, dt):
        self.timer += dt

        if self.trigger_type[0] == "time":
            if self.timer > self.trigger_type[1]:
                self.timer = 0
                self.trigger()

        if (self.trigger_type[0] == "prox") and (self.timer >= 0):
            for entity in self._game.combat.all_entities:
                if (
                    entity.raw_dis((self.loc[0] + self.size[0] // 2, self.loc[1] + self.size[1] // 2))
                    < self.trigger_type[1]
                ):
                    self.trigger()
                    self.timer = -self.prox_reset_time if self.prox_reset_time != -1 else -99999999999

        if self.is_triggered:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_dur:
                if (self.prox_reset_time == -1) and (self.trigger_type[0] == "prox"):
                    self.animation_timer -= dt
                else:
                    self.animation_timer = 0
                    self.is_triggered = False

    def draw(self, surf, offset=(0, 0)):
        img_count = len(self._game.assets.trap_animations[self.type]) - 1
        if self.animation_timer == 0:
            img = self._game.assets.trap_animations[self.type][0]
        else:
            img_idx = int(self.animation_timer / self.animation_dur * img_count)
            img = self._game.assets.trap_animations[self.type][img_idx + 1]
        self.size = list(img.get_size())
        surf.blit(img, (self.loc[0] + offset[0], self.loc[1] + offset[1]))


class SpinningBlades(Trap):
    def __init__(self, game, loc):
        super().__init__(game, loc, "spinning_blades", trigger=("time", 1))

    def trigger(self):
        super().trigger()
        for entity in self._game.combat.all_entities:
            if entity.raw_dis((self.loc[0] + self.size[0] // 2, self.loc[1] + self.size[1] // 2)) < self.size[0] // 2:
                entity.deal_damage(1, owner=entity)


class Pit(Trap):
    def __init__(self, game, loc):
        super().__init__(game, loc, "pit", trigger=("prox", 8))

    def trigger(self):
        super().trigger()
        for entity in self._game.combat.all_entities:
            if entity.raw_dis((self.loc[0] + self.size[0] // 2, self.loc[1] + self.size[1] // 2)) < self.size[0] // 2:
                entity.deal_damage(1, owner=entity)
                for entity2 in entity.unit.entities:
                    if entity2 == entity:
                        entity.unit.entities.remove(entity)


trap_types = {
    "spinning_blades": SpinningBlades,
    "pit": Pit,
}
