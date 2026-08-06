"""
Boss Enemy Module
=================
Defines the 3-Phase Ultimate Boss Enemy with:
- Phase 1: Tactical Ground Chase, Metall-style Armored Guard stance & counter-bursts.
- Phase 2: Blader-style Aerial Hover/Dash attacks, 5-way downward fan spreads, & minion summoning.
- Phase 3: Enraged Rage Mode, telegraphed high leap & ground slam shockwaves, 8-way radial bullet hell bursts.
"""

import pygame
import math
import random
import config
import assets
from entities.ai_base import IntelligentNPC
from entities.metall import Metall
from particles import spawn_particles

class BossPhase:
    PHASE1 = 0
    PHASE2 = 1
    PHASE3 = 2

class BossEnemy(IntelligentNPC):
    def __init__(self, x, y):
        super().__init__(x, y, 64, 64, config.NPCType.AGGRESSIVE)
        self.health = 35
        self.max_health = 35
        self.phase = BossPhase.PHASE1
        self.speed = 1.6
        self.detection_range = config.TILE_SIZE * 14
        self.attack_range = config.TILE_SIZE * 9
        self.bullets = []
        self.last_fired = 0
        self.last_guard = 0
        self.guard_duration = 1500
        self.last_slam = 0
        self.is_slimming = False
        self.telegraph_timer = 0
        self.telegraphing = False
        self.minions_to_spawn = []
        self.minions_spawned_phase2 = False
        self.flying = False

    def update_phase(self):
        """Updates boss phase based on health thresholds and handles phase transitions."""
        old_phase = self.phase
        if self.health > 24:
            self.phase = BossPhase.PHASE1
        elif self.health > 11:
            self.phase = BossPhase.PHASE2
        else:
            self.phase = BossPhase.PHASE3

        # Phase transition triggers
        if old_phase == BossPhase.PHASE1 and self.phase == BossPhase.PHASE2:
            if not self.minions_spawned_phase2:
                self.minions_spawned_phase2 = True
                self.minions_to_spawn.append(('metall', self.x - 60, self.y))
                self.minions_to_spawn.append(('blader', self.x + 80, self.y - 40))
                spawn_particles(self.centerx, self.centery, (255, 165, 0), 25, 5)

        if old_phase != BossPhase.PHASE3 and self.phase == BossPhase.PHASE3:
            spawn_particles(self.centerx, self.centery, (180, 0, 255), 35, 7)

    def face_player(self, player):
        """Updates facing direction towards player."""
        if player.centerx < self.centerx:
            self.direction = "left"
        else:
            self.direction = "right"

    def trigger_guard(self):
        """Manually triggers Metall-style Guard stance."""
        now = pygame.time.get_ticks()
        if now - self.last_guard > 3000:
            self.last_guard = now
            self.transition_to(config.NPCState.GUARD)

    def counter_attack(self, player=None):
        """Instant retaliatory bullet burst when struck or when guard deflects."""
        if player:
            self.face_player(player)
        b1 = Metall.Bullet(self, -config.METALL_BULLET_VELOCITY_Y * 1.2)
        b2 = Metall.Bullet(self, 0)
        b3 = Metall.Bullet(self, config.METALL_BULLET_VELOCITY_Y * 1.2)
        for b in [b1, b2, b3]:
            b.velocity_x *= 1.3
            self.bullets.append(b)

    def update_ai(self, player, tiles, all_npcs):
        self.update_phase()
        now = pygame.time.get_ticks()

        # Always face player position
        self.face_player(player)

        # Handle Guard State timer
        if self.state == config.NPCState.GUARD:
            self.guarding = True
            if self.time_in_state() > self.guard_duration:
                self.guarding = False
                self.transition_to(config.NPCState.ATTACK)
                self.counter_attack(player)
            return

        self.guarding = False

        # Phase 1: Periodic Guarding
        if self.phase == BossPhase.PHASE1:
            if random.random() < 0.008 and now - self.last_guard > 4000:
                self.trigger_guard()
                return

        # Phase 2: Aerial Flying Mode
        if self.phase == BossPhase.PHASE2:
            self.flying = True
            target_hover = max(config.TILE_SIZE * 4, player.y - 60)
            if self.y < target_hover:
                self.y += 1.5
            elif self.y > target_hover:
                self.y -= 1.5
        else:
            self.flying = False

        # Phase 3: Telegraphed Jump & Slam
        if self.phase == BossPhase.PHASE3 and not self.telegraphing and not self.is_slimming:
            if now - self.last_slam > 4500 and abs(self.centerx - player.centerx) < config.TILE_SIZE * 8:
                self.telegraphing = True
                self.telegraph_timer = now
                self.last_slam = now

        if self.telegraphing:
            if now - self.telegraph_timer > 700:  # 700ms warning
                self.telegraphing = False
                self.is_slimming = True
                self.velocity_y = -14
            return

        if self.is_slimming:
            self.velocity_y += config.GRAVITY * 1.2
            self.y += self.velocity_y
            for t in tiles:
                if self.colliderect(t) and self.velocity_y > 0:
                    self.y = t.y - self.height
                    self.velocity_y = 0
                    self.is_slimming = False
                    self._perform_ground_slam(player)
                    break
            return

        super().update_ai(player, tiles, all_npcs)
        # Re-enforce facing direction after FSM state processing
        self.face_player(player)

    def _patrol(self, tiles, can_see, dist_x):
        self.update_phase()
        if self.phase == BossPhase.PHASE1:
            self.x += self.patrol_direction * self.speed * 0.5
            if abs(self.x - self.patrol_start_x) > self.patrol_range:
                self.patrol_direction *= -1
            if can_see:
                self.transition_to(config.NPCState.ALERT)
        else:
            self.transition_to(config.NPCState.CHASE)

    def _perform_ground_slam(self, player):
        """Creates shockwave particles & horizontal wave bullets on slam impact."""
        spawn_particles(self.centerx, self.bottom, (255, 100, 0), 30, 6)
        b1 = Metall.Bullet(self, 0)
        b1.direction = "left"
        b1.velocity_x = -7
        b1.y = self.bottom - 12
        b2 = Metall.Bullet(self, 0)
        b2.direction = "right"
        b2.velocity_x = 7
        b2.y = self.bottom - 12
        self.bullets.extend([b1, b2])

    def _chase(self, player, tiles, can_see, dist_x):
        self.update_phase()
        self.face_player(player)
        speed_mult = 1.0 if self.phase == BossPhase.PHASE1 else (1.4 if self.phase == BossPhase.PHASE2 else 2.4)
        if self.direction == "left":
            self.x -= self.speed * speed_mult
        else:
            self.x += self.speed * speed_mult

        if dist_x < self.attack_range:
            self.transition_to(config.NPCState.ATTACK)

    def _attack(self, player, can_see, dist_x):
        self.update_phase()
        self.face_player(player)

        now = pygame.time.get_ticks()
        fire_rate = 1100 if self.phase == BossPhase.PHASE1 else (650 if self.phase == BossPhase.PHASE2 else 320)

        if now - self.last_fired > fire_rate:
            self.last_fired = now
            if self.phase == BossPhase.PHASE1:
                self.bullets.append(Metall.Bullet(self, -config.METALL_BULLET_VELOCITY_Y))
                self.bullets.append(Metall.Bullet(self, 0))
                self.bullets.append(Metall.Bullet(self, config.METALL_BULLET_VELOCITY_Y))

            elif self.phase == BossPhase.PHASE2:
                speeds_y = [-3, -1.5, 0, 1.5, 3]
                for vy in speeds_y:
                    b = Metall.Bullet(self, vy)
                    b.velocity_x *= 1.2
                    self.bullets.append(b)

            elif self.phase == BossPhase.PHASE3:
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    b = Metall.Bullet(self, 0)
                    b.velocity_x = math.cos(rad) * 5.5
                    b.velocity_y = math.sin(rad) * 5.5
                    self.bullets.append(b)

        if dist_x > self.attack_range * 1.3:
            self.transition_to(config.NPCState.CHASE)

    def draw(self, surface, camera_x):
        font = pygame.font.SysFont("Arial", 14)

        phase_colors = [(180, 50, 50), (200, 100, 0), (160, 0, 220)]
        col = phase_colors[self.phase]

        if self.telegraphing:
            flash_col = (255, 255, 0) if (pygame.time.get_ticks() // 100) % 2 == 0 else (255, 100, 0)
            pygame.draw.rect(surface, flash_col, (self.x - camera_x - 4, self.y - 4, self.width + 8, self.height + 8), 3, border_radius=6)

        if self.guarding:
            pygame.draw.rect(surface, (100, 200, 255), (self.x - camera_x - 3, self.y - 3, self.width + 6, self.height + 6), 3, border_radius=6)

        pygame.draw.rect(surface, col, (self.x - camera_x, self.y, self.width, self.height), border_radius=4)

        eye_col = (255, 255, 255) if not self.guarding else (100, 200, 255)
        if self.direction == "left":
            pygame.draw.rect(surface, eye_col, (self.x - camera_x + 8, self.y + 12, 12, 12))
            pygame.draw.rect(surface, eye_col, (self.x - camera_x + 28, self.y + 12, 12, 12))
        else:
            pygame.draw.rect(surface, eye_col, (self.x - camera_x + 24, self.y + 12, 12, 12))
            pygame.draw.rect(surface, eye_col, (self.x - camera_x + 44, self.y + 12, 12, 12))

        if self.phase == BossPhase.PHASE3 and random.random() < 0.4:
            spawn_particles(self.centerx, self.centery, (180, 0, 255), 2, 2)

        bar_w = self.width + 20
        bar_x = self.x - camera_x - 10
        hp_pct = max(0, self.health / self.max_health)

        pygame.draw.rect(surface, (40, 40, 40), (bar_x, self.y - 24, bar_w, 8))
        pygame.draw.rect(surface, col, (bar_x, self.y - 24, bar_w * hp_pct, 8))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, self.y - 24, bar_w, 8), 1)

        phase_names = ["PHASE 1: ARMORED GUARD", "PHASE 2: AERIAL STRIKE", "PHASE 3: ENRAGED RAGE"]
        txt = font.render(f"BOSS - {phase_names[self.phase]}", True, (255, 220, 220))
        surface.blit(txt, (bar_x, self.y - 42))

        for b in self.bullets:
            surface.blit(assets.metall_image_bullet, (b.x - camera_x, b.y))
