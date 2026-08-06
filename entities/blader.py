"""
Blader Enemy Module
===================
Defines the flying Blader enemy, sine/patrol flight physics,
and vertical swooping attack AI logic.
"""

import random
import config
import assets
from enemy_collision import check_enemy_tile_collision_x, check_enemy_tile_collision_y
from entities.ai_base import IntelligentNPC

class Blader(IntelligentNPC):
    def __init__(self, x, y, npc_type=None):
        if npc_type is None:
            types = [config.NPCType.AGGRESSIVE, config.NPCType.GUARD, config.NPCType.COWARD]
            weights = [0.45, 0.40, 0.15]
            npc_type = random.choices(types, weights=weights)[0]
        super().__init__(x, y, config.BLADER_WIDTH, config.BLADER_HEIGHT, npc_type)
        self.image = assets.blader_image_right
        self.direction = "right"
        self.health = 3
        self.max_health = 3
        self.velocity_x = config.BLADER_VELOCITY_X
        self.velocity_y = config.BLADER_VELOCITY_Y
        self.start_x = x
        self.start_y = y
        self.max_range_x = config.TILE_SIZE * 4
        self.max_range_y = config.TILE_SIZE
        self.speed = config.BLADER_VELOCITY_X
        self.detection_range = config.TILE_SIZE * 8

    def update_image(self):
        if self.direction == "right":
            self.image = assets.blader_image_right
        elif self.direction == "left":
            self.image = assets.blader_image_left

    def _patrol(self, tiles, can_see, dist_x):
        if abs(self.x + self.velocity_x - self.start_x) >= self.max_range_x:
            self.velocity_x *= -1
            self.direction = "left" if self.velocity_x < 0 else "right"
        elif check_enemy_tile_collision_x(self, self.velocity_x, tiles):
            self.velocity_x *= -1
            self.direction = "left" if self.velocity_x < 0 else "right"

        if abs(self.y + self.velocity_y - self.start_y) >= self.max_range_y:
            self.velocity_y *= -1
        elif check_enemy_tile_collision_y(self, self.velocity_y, tiles):
            self.velocity_y *= -1

        if can_see:
            self.transition_to(config.NPCState.ALERT)

    def _chase(self, player, tiles, can_see, dist_x):
        dx = -self.speed * 1.3 if player.centerx < self.centerx else self.speed * 1.3
        self.direction = "left" if dx < 0 else "right"
        check_enemy_tile_collision_x(self, dx, tiles)

        dy = -self.speed * 0.8 if player.centery < self.centery else self.speed * 0.8
        check_enemy_tile_collision_y(self, dy, tiles)

        if dist_x < config.TILE_SIZE * 2:
            self.transition_to(config.NPCState.ATTACK)
        if not can_see and self.time_in_state() > 2000:
            self.transition_to(config.NPCState.PATROL)

    def _attack(self, player, can_see, dist_x):
        dy = self.speed * 2.5 if self.time_in_state() < 400 else -self.speed
        # Tile collision check in vertical attack
        from game_manager import tiles
        check_enemy_tile_collision_y(self, dy, tiles)
        if self.time_in_state() > 800:
            self.transition_to(config.NPCState.RETREAT)

    def _retreat(self, player, tiles):
        if abs(self.x - self.start_x) > 10:
            if self.start_x < self.x:
                self.x -= self.speed
                self.direction = "left"
            else:
                self.x += self.speed
                self.direction = "right"
        if abs(self.y - self.start_y) > 10:
            if self.start_y < self.y:
                self.y -= self.speed
            else:
                self.y += self.speed
        if abs(self.x - self.start_x) < 30 and abs(self.y - self.start_y) < 30:
            self.transition_to(config.NPCState.PATROL)
