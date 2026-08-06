"""
Asset Manager Module
====================
Handles image loading with procedural fallback surfaces for missing files.
Provides loaded Pygame image surfaces for players, enemies, tiles, and items.
"""

# pyrefly: ignore [missing-import]
import pygame
import os
import config

def load_image(image_name, scale=None):
    """Loads an image from the images directory, scaling if specified, or returns a fallback surface."""
    try:
        image = pygame.image.load(os.path.join("images", image_name))
        if scale is not None:
            image = pygame.transform.scale(image, scale)
        return image
    except Exception:
        surf = pygame.Surface(scale or (32, 32))
        surf.fill((128, 128, 128))
        return surf

# --- Background & Player Sprites ---
background_image = load_image("background.png")
player_image_right = load_image("megaman-right.png", (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
player_image_left = load_image("megaman-left.png", (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
player_image_jump_right = load_image("megaman-right-jump.png", (config.PLAYER_JUMP_WIDTH, config.PLAYER_JUMP_HEIGHT))
player_image_jump_left = load_image("megaman-left-jump.png", (config.PLAYER_JUMP_WIDTH, config.PLAYER_JUMP_HEIGHT))
player_image_shoot_right = load_image("megaman-right-shoot.png", (config.PLAYER_SHOOT_WIDTH, config.PLAYER_HEIGHT))
player_image_shoot_left = load_image("megaman-left-shoot.png", (config.PLAYER_SHOOT_WIDTH, config.PLAYER_HEIGHT))
player_image_jump_shoot_right = load_image("megaman-right-jump-shoot.png", (config.PLAYER_JUMP_SHOOT_WIDTH, config.PLAYER_JUMP_HEIGHT))
player_image_jump_shoot_left = load_image("megaman-left-jump-shoot.png", (config.PLAYER_JUMP_SHOOT_WIDTH, config.PLAYER_JUMP_HEIGHT))
player_image_bullet = load_image("bullet.png", (config.PLAYER_BULLET_WIDTH, config.PLAYER_BULLET_HEIGHT))

player_image_walk_right = [load_image(f"megaman-right-walk{i}.png", (config.PLAYER_WALK_WIDTH, config.PLAYER_WALK_HEIGHT)) for i in range(4)]
player_image_walk_left = [load_image(f"megaman-left-walk{i}.png", (config.PLAYER_WALK_WIDTH, config.PLAYER_WALK_HEIGHT)) for i in range(4)]
player_image_walk_shoot_right = [load_image(f"megaman-right-walk-shoot{i}.png", (config.PLAYER_WALK_SHOOT_WIDTH, config.PLAYER_WALK_HEIGHT)) for i in range(4)]
player_image_walk_shoot_left = [load_image(f"megaman-left-walk-shoot{i}.png", (config.PLAYER_WALK_SHOOT_WIDTH, config.PLAYER_WALK_HEIGHT)) for i in range(4)]

# --- Tile Sprites ---
floor_tile_image = load_image("floor-tile.png", (config.TILE_SIZE, config.TILE_SIZE))
wall_tile_image = load_image("wall-tile.png", (config.TILE_SIZE, config.TILE_SIZE))
beam_tile_image = load_image("beam-tile.png", (config.TILE_SIZE, config.TILE_SIZE))
rock_tile1_image = load_image("rock-tile1.png", (config.TILE_SIZE, config.TILE_SIZE))
rock_tile2_image = load_image("rock-tile2.png", (config.TILE_SIZE, config.TILE_SIZE))
rock_tile3_image = load_image("rock-tile3.png", (config.TILE_SIZE, config.TILE_SIZE))
rock_tile4_image = load_image("rock-tile4.png", (config.TILE_SIZE, config.TILE_SIZE))
door_tile_image = load_image("door-tile.png", (config.TILE_SIZE, config.TILE_SIZE))
room_tile_image = load_image("room-tile.png", (config.TILE_SIZE, config.TILE_SIZE))

# --- Enemy & Item Sprites ---
metall_image_right = load_image("metall-right.png", (config.METALL_WIDTH, config.METALL_HEIGHT))
metall_image_left = load_image("metall-left.png", (config.METALL_WIDTH, config.METALL_HEIGHT))
metall_image_guard_right = load_image("metall-right-guard.png", (config.METALL_WIDTH, config.METALL_HEIGHT))
metall_image_guard_left = load_image("metall-left-guard.png", (config.METALL_WIDTH, config.METALL_HEIGHT))
metall_image_bullet = load_image("metall-bullet.png", (config.METALL_BULLET_WIDTH, config.METALL_BULLET_HEIGHT))

health_image = load_image("health.png", (config.HEALTH_WIDTH, config.HEALTH_HEIGHT))
life_energy_image = load_image("life-energy.png", (config.LIFE_ENERGY_WIDTH, config.LIFE_ENERGY_HEIGHT))
big_life_energy_image = load_image("big-life-energy.png", (config.BIG_LIFE_ENERGY_WIDTH, config.BIG_LIFE_ENERGY_HEIGHT))
score_ball_image = load_image("score-ball.png", (config.TILE_SIZE // 2, config.TILE_SIZE // 2))
spike_image = load_image("spike.png", (config.TILE_SIZE, config.TILE_SIZE))
blader_image_right = load_image("blader-right.png", (config.BLADER_WIDTH, config.BLADER_HEIGHT))
blader_image_left = load_image("blader-left.png", (config.BLADER_WIDTH, config.BLADER_HEIGHT))
