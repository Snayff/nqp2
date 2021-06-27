import math


class Hitbox:
    def __init__(self, entities, shape_type, shape_data, damage, owner=None, friendly_fire=False):
        self.entities = entities
        self.shape_type = shape_type
        self.shape_data = shape_data
        self.damage = damage
        self.owner = owner
        self.friendly_fire = friendly_fire

    def apply(self):
        for entity in self.entities:
            if (not self.friendly_fire) or (entity.team != owner.team):
                hit = False
                if self.shape_type == "circle":
                    dis = math.sqrt(
                        (entity.pos[0] - self.shape_data[0][0]) ** 2 + (entity.pos[1] - self.shape_data[0][1]) ** 2
                    )
                    if dis < self.shape_data[1]:
                        hit = True
                if self.shape_type == "rect":
                    if self.shape_data.collidepoint(entity.pos):
                        hit = True

                if hit:
                    entity.deal_damage(self.damage, self.owner)
