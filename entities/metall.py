"""
Metall Enemy Module
===================
Defines the Metall enemy, its projectile weapons, sprite animations,
and counter-attacking AI behavior.
"""
# pyrefly: ignore [missing-import]
import pygame
import random
import config
import assets
from entities.ai_base import IntelligentNPC

class Metall(IntelligentNPC):
    class Bullet(pygame.Rect):
        def __init__(self, metall, velocity_y):
            if metall.direction == "left":
                super().__init__(metall.x, metall.y + config.TILE_SIZE / 2,
                                 config.METALL_BULLET_WIDTH, config.METALL_BULLET_HEIGHT)
                self.velocity_x = -config.METALL_BULLET_VELOCITY_X
            elif metall.direction == "right":
                super().__init__(metall.x + metall.width, metall.y + config.TILE_SIZE / 2,
                                 config.METALL_BULLET_WIDTH, config.METALL_BULLET_HEIGHT)
                self.velocity_x = config.METALL_BULLET_VELOCITY_X
            self.velocity_y = velocity_y
            self.image = assets.metall_image_bullet
            self.used = False

    def __init__(self, x, y, npc_type=None):
        if npc_type is None:
            types = [config.NPCType.GUARD, config.NPCType.AGGRESSIVE, config.NPCType.COWARD]
            weights = [0.50, 0.35, 0.15]
            npc_type = random.choices(types, weights=weights)[0]
        super().__init__(x, y, config.METALL_WIDTH, config.METALL_HEIGHT, npc_type)
        self.image = assets.metall_image_left
        self.velocity_y = 0
        self.direction = "left"
        self.health = 3
        self.max_health = 3
        self.bullets = []
        self.last_fired = pygame.time.get_ticks()
        self.guarding = False
        self.speed = 1.2
        self.patrol_range = config.TILE_SIZE * 2.5

    def update_image(self):
        if self.direction == "right":
            if self.state in [config.NPCState.GUARD, config.NPCState.RETREAT]:
                self.image = assets.metall_image_guard_right
            else:
                self.image = assets.metall_image_right
        elif self.direction == "left":
            if self.state in [config.NPCState.GUARD, config.NPCState.RETREAT]:
                self.image = assets.metall_image_guard_left
            else:
                self.image = assets.metall_image_left

    def take_damage(self, amount):
        """When shot while un-guarded, Metall counter-attacks directly."""
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            if self.health > 0:
                self.transition_to(config.NPCState.ATTACK)

    def _attack(self, player, can_see, dist_x):
        if player.centerx < self.centerx:
            self.direction = "left"
        else:
            self.direction = "right"
        now = pygame.time.get_ticks()
        if now - self.last_fired > 900:
            self.last_fired = now
            self.bullets.append(Metall.Bullet(self, -config.METALL_BULLET_VELOCITY_Y))
            self.bullets.append(Metall.Bullet(self, 0))
            self.bullets.append(Metall.Bullet(self, config.METALL_BULLET_VELOCITY_Y))
        if dist_x > self.attack_range * 1.2:
            self.transition_to(config.NPCState.CHASE)
