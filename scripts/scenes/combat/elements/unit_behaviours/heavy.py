from .base import Base


class Heavy(Base):
    def complete_init(self):
        super().complete_init()

        self.force_regroup = True

        if self.unit.use_ammo:
            self.smart_range_retarget = True

    def process(self, dt):
        super().process(dt)
