"""
Base Intelligent NPC Engine
===========================
Defines the IntelligentNPC base class containing Finite State Machine (FSM)
state transitions, line-of-sight tile raycasting, decision trees, and AI overlays.
"""
# pyrefly: ignore [missing-import]
import pygame
import random
import config
from enemy_collision import check_enemy_tile_collision_x

pygame.font.init()
small_font = pygame.font.SysFont("Arial", 14)

class IntelligentNPC(pygame.Rect):
    def __init__(self, x, y, width, height, npc_type):
        super().__init__(x, y, width, height)
        self.npc_type = npc_type
        self.state = config.NPCState.PATROL
        self.state_start_time = pygame.time.get_ticks()
        self.alert_level = 0
        self.patrol_start_x = x
        self.patrol_range = config.PATROL_RANGE
        self.patrol_direction = -1 if random.random() < 0.5 else 1
        self.health = 1
        self.max_health = 1
        self.invincible = False
        self.invincible_timer = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 2
        self.detection_range = config.DETECTION_RANGE
        self.attack_range = config.ATTACK_RANGE
        self.direction = "left"
        self.guarding = False

    def time_in_state(self):
        return pygame.time.get_ticks() - self.state_start_time

    def transition_to(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = pygame.time.get_ticks()

    def can_see_player(self, player, tiles):
        """Raycasts between enemy and player to check for tile line-of-sight blockages."""
        dist_x = abs(self.centerx - player.centerx)
        dist_y = abs(self.centery - player.centery)
        if dist_x > self.detection_range or dist_y > config.TILE_SIZE * 4:
            return False
        step = config.TILE_SIZE // 2
        start_x = min(self.centerx, player.centerx)
        end_x = max(self.centerx, player.centerx)
        check_y = self.centery
        for x in range(int(start_x), int(end_x), step):
            check_rect = pygame.Rect(x, check_y - config.TILE_SIZE // 2, config.TILE_SIZE // 2, config.TILE_SIZE)
            for tile in tiles:
                if tile.colliderect(check_rect):
                    return False
        return True

    def update_ai(self, player, tiles, all_npcs):
        """Main AI decision loop evaluated every frame."""
        can_see = self.can_see_player(player, tiles)
        dist_x = abs(self.centerx - player.centerx)

        if can_see:
            self.alert_level = min(100, self.alert_level + 2)
        else:
            self.alert_level = max(0, self.alert_level - 1)

        if self.state == config.NPCState.PATROL:
            self._patrol(tiles, can_see, dist_x)
        elif self.state == config.NPCState.ALERT:
            self._alert(can_see, dist_x)
        elif self.state == config.NPCState.CHASE:
            self._chase(player, tiles, can_see, dist_x)
        elif self.state == config.NPCState.ATTACK:
            self._attack(player, can_see, dist_x)
        elif self.state == config.NPCState.RETREAT:
            self._retreat(player, tiles)
        elif self.state == config.NPCState.FLEE:
            self._flee(player, tiles)
        elif self.state == config.NPCState.GUARD:
            self._guard(can_see, dist_x)
        elif self.state == config.NPCState.IDLE:
            self._idle(tiles, can_see, dist_x)

    def _patrol(self, tiles, can_see, dist_x):
        dx = self.patrol_direction * self.speed
        if check_enemy_tile_collision_x(self, dx, tiles):
            self.patrol_direction *= -1
        elif abs(self.x - self.patrol_start_x) > self.patrol_range:
            self.patrol_direction *= -1
        self.direction = "left" if self.patrol_direction < 0 else "right"
        if can_see and dist_x < self.detection_range:
            self.transition_to(config.NPCState.ALERT)

    def _alert(self, can_see, dist_x):
        self.velocity_x = 0
        if self.time_in_state() > 500:
            if self.npc_type == config.NPCType.COWARD:
                self.transition_to(config.NPCState.FLEE)
            else:
                self.transition_to(config.NPCState.CHASE)
        if not can_see and self.time_in_state() > 1000:
            self.transition_to(config.NPCState.PATROL)

    def _chase(self, player, tiles, can_see, dist_x):
        if player.centerx < self.centerx:
            dx = -self.speed * 1.5
            self.direction = "left"
        else:
            dx = self.speed * 1.5
            self.direction = "right"
        check_enemy_tile_collision_x(self, dx, tiles)
        if dist_x < self.attack_range:
            self.transition_to(config.NPCState.ATTACK)
        if not can_see and self.time_in_state() > 2000:
            self.transition_to(config.NPCState.PATROL)

    def _attack(self, player, can_see, dist_x):
        if dist_x > self.attack_range * 1.2:
            self.transition_to(config.NPCState.CHASE)
        elif self.time_in_state() > 800:
            if self.npc_type != config.NPCType.AGGRESSIVE:
                self.transition_to(config.NPCState.RETREAT)

    def _retreat(self, player, tiles):
        if player.centerx < self.centerx:
            dx = self.speed
            self.direction = "right"
        else:
            dx = -self.speed
            self.direction = "left"
        check_enemy_tile_collision_x(self, dx, tiles)
        if self.time_in_state() > 1000:
            if self.npc_type == config.NPCType.GUARD:
                self.transition_to(config.NPCState.GUARD)
            else:
                self.transition_to(config.NPCState.PATROL)

    def _flee(self, player, tiles):
        if player.centerx < self.centerx:
            dx = self.speed * 1.5
            self.direction = "right"
        else:
            dx = -self.speed * 1.5
            self.direction = "left"
        check_enemy_tile_collision_x(self, dx, tiles)
        if abs(self.centerx - player.centerx) > self.detection_range * 1.5:
            self.transition_to(config.NPCState.PATROL)

    def _guard(self, can_see, dist_x):
        self.velocity_x = 0
        self.guarding = True
        if can_see and dist_x < self.detection_range:
            self.transition_to(config.NPCState.ALERT)

    def _idle(self, tiles, can_see, dist_x):
        self.velocity_x = 0
        if can_see:
            self.transition_to(config.NPCState.ALERT)
        elif self.time_in_state() > 2000:
            self.transition_to(config.NPCState.PATROL)

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            if self.health > 0:
                if self.npc_type == config.NPCType.COWARD:
                    self.transition_to(config.NPCState.FLEE)
                elif self.npc_type == config.NPCType.AGGRESSIVE:
                    self.transition_to(config.NPCState.ATTACK)
                else:
                    self.transition_to(config.NPCState.RETREAT)

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.invincible_timer > 400:
            self.invincible = False

    def draw_ai_overlay(self, surface, camera_x):
        color = config.STATE_COLORS.get(self.state, (255, 255, 255))
        pygame.draw.circle(surface, color, (self.centerx - camera_x, self.y - 8), 4)
        letter = config.NPC_TYPE_NAMES.get(self.npc_type, "?")
        txt = small_font.render(letter, True, (255, 255, 255))
        surface.blit(txt, (self.centerx - camera_x - 4, self.y - 20))
        if self.health < self.max_health:
            bar_w = self.width
            hp_pct = max(0, self.health / self.max_health)
            pygame.draw.rect(surface, (200, 0, 0), (self.x - camera_x, self.y - 14, bar_w, 4))
            pygame.draw.rect(surface, (0, 200, 0), (self.x - camera_x, self.y - 14, bar_w * hp_pct, 4))
