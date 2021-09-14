from .base import Base

class Light(Base):
    def complete_init(self):
        super().complete_init()

    def process(self, dt):
        super().process(dt)
