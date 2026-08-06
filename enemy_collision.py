"""
Enemy Collision Module
======================
Handles tile and wall collisions for ground and flying enemies to prevent them 
from entering or clipping through solid map tiles.
"""
# pyrefly: ignore [missing-import]
import pygame

def check_enemy_tile_collision_x(enemy, dx, tiles):
    """
    Moves an enemy horizontally by dx and resolves any tile collisions.
    Returns True if a wall collision occurred, False otherwise.
    """
    if dx == 0:
        return False

    enemy.x += dx
    hit_wall = False

    for tile in tiles:
        if enemy.colliderect(tile):
            hit_wall = True
            if dx > 0:  # Moving right -> hit left side of tile
                enemy.x = tile.x - enemy.width
            elif dx < 0:  # Moving left -> hit right side of tile
                enemy.x = tile.x + tile.width
            break

    return hit_wall


def check_enemy_tile_collision_y(enemy, dy, tiles):
    """
    Moves an enemy vertically by dy and resolves any tile collisions.
    Returns True if a ceiling or floor collision occurred, False otherwise.
    """
    if dy == 0:
        return False

    enemy.y += dy
    hit_tile = False

    for tile in tiles:
        if enemy.colliderect(tile):
            hit_tile = True
            if dy > 0:  # Falling / moving down -> hit top of tile
                enemy.y = tile.y - enemy.height
                if hasattr(enemy, 'velocity_y'):
                    enemy.velocity_y = 0
            elif dy < 0:  # Jumping / moving up -> hit bottom of tile
                enemy.y = tile.y + tile.height
                if hasattr(enemy, 'velocity_y'):
                    enemy.velocity_y = 0
            break

    return hit_tile


def resolve_enemy_wall_overlap(enemy, tiles):
    """
    Checks if an enemy is currently overlapping any tile and pushes it out.
    Used after state transitions or manual position adjustments.
    """
    for tile in tiles:
        if enemy.colliderect(tile):
            overlap_left = (enemy.x + enemy.width) - tile.x
            overlap_right = (tile.x + tile.width) - enemy.x
            overlap_top = (enemy.y + enemy.height) - tile.y
            overlap_bottom = (tile.y + tile.height) - enemy.y

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                enemy.x = tile.x - enemy.width
            elif min_overlap == overlap_right:
                enemy.x = tile.x + tile.width
            elif min_overlap == overlap_top:
                enemy.y = tile.y - enemy.height
                if hasattr(enemy, 'velocity_y'):
                    enemy.velocity_y = 0
            elif min_overlap == overlap_bottom:
                enemy.y = tile.y + tile.height
                if hasattr(enemy, 'velocity_y'):
                    enemy.velocity_y = 0
