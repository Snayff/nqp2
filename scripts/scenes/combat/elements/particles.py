import math
import random

class Particle:
    def __init__(self, loc, vel, dur, color):
        self.loc = list(loc)
        self.vel = list(vel)
        self.dur = dur
        self.color = color

    def update(self, dt):
        self.loc[0] += self.vel[0] * dt
        self.loc[1] += self.vel[1] * dt

        self.dur -= dt
        if self.dur < 0:
            return False
        return True

    def render(self, surf, offset=(0, 0)):
        surf.set_at((int(self.loc[0] + offset[0]), int(self.loc[1] + offset[1])), self.color)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_particle_burst(self, loc, color, count, speed_range=[30, 60], dur_range=[0.2, 0.3]):
        for i in range(count):
            speed = random.random() * (speed_range[1] - speed_range[0]) + speed_range[0]
            dur = random.random() * (dur_range[1] - dur_range[0]) + dur_range[0]
            angle = random.random() * math.pi * 2
            p = Particle(loc, [math.cos(angle) * speed, math.sin(angle) * speed], dur, color)
            self.particles.append(p)

    def update(self, dt):
        for i, p in sorted(enumerate(self.particles), reverse=True):
            if not p.update(dt):
                self.particles.pop(i)

    def render(self, surf, offset=(0, 0)):
        for p in self.particles:
            p.render(surf, offset=offset)
