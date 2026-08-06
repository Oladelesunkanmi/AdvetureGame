"""
Interactive Objects Module
==========================
Defines interactive world elements including Tiles, Pickups, Checkpoints,
Key Items, Locked Doors, and Friendly NPCs.
"""
# pyrefly: ignore [missing-import]
import pygame
import math
import random
import config

# Fonts for interactive object labels
pygame.font.init()
small_font = pygame.font.SysFont("Arial", 14)

class Tile(pygame.Rect):
    def __init__(self, x, y, image):
        super().__init__(x, y, config.TILE_SIZE, config.TILE_SIZE)
        self.image = image

class Item(pygame.Rect):
    def __init__(self, x, y, image):
        super().__init__(x, y, image.get_width(), image.get_height())
        self.image = image
        self.jumping = False
        self.velocity_y = config.ITEM_VELOCITY_Y
        self.used = False

class Checkpoint(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, config.TILE_SIZE, config.TILE_SIZE)
        self.activated = False
        self.pulse = 0

    def draw(self, surface, camera_x):
        self.pulse += 0.1
        glow = int(8 + math.sin(self.pulse) * 4)
        color = (100, 255, 100) if self.activated else (150, 150, 150)
        s = pygame.Surface((config.TILE_SIZE + glow * 2, config.TILE_SIZE + glow * 2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 80), (0, 0, config.TILE_SIZE + glow * 2, config.TILE_SIZE + glow * 2), border_radius=4)
        surface.blit(s, (self.x - camera_x - glow, self.y - glow))
        pygame.draw.rect(surface, color, (self.x - camera_x, self.y, config.TILE_SIZE, config.TILE_SIZE), border_radius=2)
        pygame.draw.rect(surface, (50, 50, 50), (self.x - camera_x + 4, self.y + 4, config.TILE_SIZE - 8, config.TILE_SIZE - 8), border_radius=2)
        if self.activated:
            txt = small_font.render("SAVE", True, (255, 255, 255))
            surface.blit(txt, (self.x - camera_x + 2, self.y - 14))

class KeyItem(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.collected = False
        self.bob = random.random() * 6.28

    def draw(self, surface, camera_x):
        if self.collected:
            return
        self.bob += 0.05
        by = self.y + math.sin(self.bob) * 3
        pygame.draw.circle(surface, config.C_GOLD, (int(self.x - camera_x + 10), int(by + 10)), 8)
        pygame.draw.circle(surface, (255, 255, 150), (int(self.x - camera_x + 10), int(by + 10)), 5)
        pygame.draw.circle(surface, (200, 170, 0), (int(self.x - camera_x + 6), int(by + 6)), 2)

class LockedDoor(pygame.Rect):
    def __init__(self, x, y, is_exit=False, locked=True):
        super().__init__(x, y, config.TILE_SIZE, config.TILE_SIZE)
        self.locked = locked
        self.is_exit = is_exit

    def draw(self, surface, camera_x):
        if self.locked:
            color = (139, 69, 19) if not self.is_exit else (180, 50, 50)
            pygame.draw.rect(surface, color, (self.x - camera_x, self.y, config.TILE_SIZE, config.TILE_SIZE))
            pygame.draw.rect(surface, (80, 40, 10), (self.x - camera_x + 4, self.y + 4, config.TILE_SIZE - 8, config.TILE_SIZE - 8))
            pygame.draw.rect(surface, config.C_GOLD, (self.x - camera_x + 10, self.y + 12, 12, 10))
            pygame.draw.circle(surface, config.C_GOLD, (self.x - camera_x + 16, self.y + 10), 4)
        else:
            color = (60, 40, 20) if not self.is_exit else (50, 200, 50)
            pygame.draw.rect(surface, color, (self.x - camera_x, self.y, config.TILE_SIZE, config.TILE_SIZE))
            pygame.draw.rect(surface, (30, 20, 10), (self.x - camera_x + 2, self.y + 2, config.TILE_SIZE - 4, config.TILE_SIZE - 4))
            if self.is_exit:
                txt = small_font.render("EXIT", True, (255, 255, 255))
                surface.blit(txt, (self.x - camera_x, self.y - 14))

class FriendlyNPC(pygame.Rect):
    def __init__(self, x, y, name, dialogues):
        super().__init__(x, y, 32, 48)
        self.name = name
        self.dialogues = dialogues
        self.current_dialogue = 0
        self.talked = False
        self.bob = 0

    def get_dialogue(self):
        if self.current_dialogue < len(self.dialogues):
            text = self.dialogues[self.current_dialogue]
            self.current_dialogue = min(self.current_dialogue + 1, len(self.dialogues) - 1)
            return text
        return self.dialogues[-1] if self.dialogues else "..."

    def draw(self, surface, camera_x):
        self.bob += 0.05
        by = self.y + math.sin(self.bob) * 2
        pygame.draw.rect(surface, (100, 150, 200), (self.x - camera_x, by, 32, 40))
        pygame.draw.circle(surface, (255, 220, 180), (self.x - camera_x + 16, int(by) - 8), 10)
        txt = small_font.render(self.name, True, (255, 255, 255))
        surface.blit(txt, (self.x - camera_x, int(by) - 24))
        if not self.talked:
            pygame.draw.polygon(surface, (255, 255, 0), [
                (self.x - camera_x + 16, int(by) - 28),
                (self.x - camera_x + 12, int(by) - 36),
                (self.x - camera_x + 20, int(by) - 36)
            ])
