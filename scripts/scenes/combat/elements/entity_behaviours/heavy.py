from .base import Base

class Heavy(Base):
    def complete_init(self):
        super().complete_init()

    def process(self, dt):
        super().process(dt)
