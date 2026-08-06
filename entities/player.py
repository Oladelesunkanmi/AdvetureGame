"""
Player Entity Module
====================
Defines the Player class, movement physics, bullet creation, walk animation,
health, invincibility timers, and XP leveling.
"""

import pygame
import config
import assets
from particles import spawn_particles

class Player(pygame.Rect):
    class Bullet(pygame.Rect):
        def __init__(self, player):
            if player.direction == "left":
                super().__init__(player.x, player.y + config.TILE_SIZE / 2,
                                 config.PLAYER_BULLET_WIDTH, config.PLAYER_BULLET_HEIGHT)
                self.velocity_x = -config.PLAYER_BULLET_VELOCITY_X
            elif player.direction == "right":
                super().__init__(player.x + player.width, player.y + config.TILE_SIZE / 2,
                                 config.PLAYER_BULLET_WIDTH, config.PLAYER_BULLET_HEIGHT)
                self.velocity_x = config.PLAYER_BULLET_VELOCITY_X
            self.image = assets.player_image_bullet
            self.used = False

    def __init__(self):
        super().__init__(config.PLAYER_X, config.PLAYER_Y, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        self.image = assets.player_image_right
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "right"
        self.jumping = False
        self.invincible = False
        self.max_health = 50
        self.health = self.max_health
        self.shooting = False
        self.bullets = []
        self.score = 0
        self.walking = False
        self.current_walk_index = 0
        self.last_updated_walk_index = pygame.time.get_ticks()
        self.level = 1
        self.xp = 0
        self.xp_to_next = config.XP_TO_LEVEL[1] if len(config.XP_TO_LEVEL) > 1 else 100
        self.damage = 1
        self.keys_found = 0

    def gain_xp(self, amount):
        """Grants XP to the player and handles leveling up."""
        self.xp += amount
        self.score += amount
        if self.xp >= self.xp_to_next and self.level < len(config.XP_TO_LEVEL) - 1:
            self.level += 1
            self.xp -= self.xp_to_next
            self.xp_to_next = config.XP_TO_LEVEL[self.level] if self.level < len(config.XP_TO_LEVEL) else self.xp_to_next * 1.5
            self.max_health += 5
            self.health = self.max_health
            self.damage += 1
            spawn_particles(self.centerx, self.centery, config.C_GOLD, 20, 5)

    def update_image(self):
        """Updates the current sprite frame based on movement, jump, and shoot state."""
        if self.walking and not self.jumping:
            if self.shooting:
                if self.direction == "right":
                    self.image = assets.player_image_walk_shoot_right[self.current_walk_index]
                elif self.direction == "left":
                    self.image = assets.player_image_walk_shoot_left[self.current_walk_index]
            else:
                if self.direction == "right":
                    self.image = assets.player_image_walk_right[self.current_walk_index]
                elif self.direction == "left":
                    self.image = assets.player_image_walk_left[self.current_walk_index]
            self.update_walking_animation()
        else:
            self.current_walk_index = 0
            if self.jumping and self.shooting:
                if self.direction == "right":
                    self.image = assets.player_image_jump_shoot_right
                elif self.direction == "left":
                    self.image = assets.player_image_jump_shoot_left
            elif self.shooting:
                if self.direction == "right":
                    self.image = assets.player_image_shoot_right
                elif self.direction == "left":
                    self.image = assets.player_image_shoot_left
            elif self.jumping:
                if self.direction == "right":
                    self.image = assets.player_image_jump_right
                elif self.direction == "left":
                    self.image = assets.player_image_jump_left
            else:
                if self.direction == "right":
                    self.image = assets.player_image_right
                elif self.direction == "left":
                    self.image = assets.player_image_left

    def update_walking_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_updated_walk_index > 250:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(assets.player_image_walk_right)

    def set_invincible(self, milliseconds=1000):
        self.invincible = True
        pygame.time.set_timer(config.INVINCIBLE_END, milliseconds, 1)

    def set_shooting(self):
        if not self.shooting:
            self.shooting = True
            self.bullets.append(Player.Bullet(self))
            pygame.time.set_timer(config.SHOOTING_END, 250, 1)
