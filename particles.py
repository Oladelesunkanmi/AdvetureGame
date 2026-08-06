"""
Particle Effects System
=======================
Handles visual particle creation, physics updates, fading, and rendering.
"""

import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity_x
        self.vy = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity effect
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera_x=0):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - camera_x - self.size), int(self.y - self.size)))

particles = []

def spawn_particles(x, y, color, count=8, speed=3):
    """Spawns radial particles at (x, y) with specified color, count, and speed."""
    for _ in range(count):
        angle = random.uniform(0, 6.28)
        spd = random.uniform(1, speed)
        particles.append(Particle(x, y, color,
                                   math.cos(angle) * spd,
                                   math.sin(angle) * spd - 2,
                                   random.randint(15, 30),
                                   random.randint(2, 5)))
