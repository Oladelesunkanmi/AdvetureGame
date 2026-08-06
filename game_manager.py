"""
Game Manager Module
===================
Orchestrates stage loading, map creation, collision logic, entity updates,
rendering pipeline, and game loop state.
"""
# pyrefly: ignore [missing-import]
import pygame
import random
import math

import config
import assets
import tile_map
from particles import particles, spawn_particles
from systems.quest import Quest, active_quests, completed_quests, add_quest, update_quests
from systems.inventory import Inventory
from systems.interactive import Checkpoint, KeyItem, LockedDoor, FriendlyNPC, Tile, Item
from entities.player import Player
from entities.metall import Metall
from entities.blader import Blader
from entities.boss import BossEnemy

pygame.font.init()
game_font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 14)
dialogue_font = pygame.font.SysFont("Arial", 18)

# --- Global Game State & Collections ---
current_stage_num = 1
max_stages = 3
stage_banner_timer = 0
stage_banner_text = ""
STAGE_NAMES = {
    1: "Stage 1-1: Grassland Corridor",
    2: "Stage 1-2: Underground Cavern",
    3: "Stage 1-3: Boss Fortress Arena"
}

stage_total_enemies = 0
stage_enemies_killed = 0
KILL_REQUIREMENT_PCT = 0.70

game_over = False
player = Player()
metalls = []
metall_bullets = []
tiles = []
background_tiles = []
items = []
spikes = []
bladers = []
checkpoints = []
last_checkpoint = None
keys = []
doors = []
friendly_npcs = []
current_dialogue = None
dialogue_timer = 0
boss = None
inventory = Inventory()
show_inventory = False

def get_kill_progress():
    """Returns (killed, total, percentage) for current stage."""
    if stage_total_enemies == 0:
        return 0, 0, 1.0
    pct = stage_enemies_killed / stage_total_enemies
    return stage_enemies_killed, stage_total_enemies, pct

def check_exit_door_unlock():
    """Unlocks exit doors if 70% kill requirement is met."""
    killed, total, pct = get_kill_progress()
    if pct >= KILL_REQUIREMENT_PCT:
        for door in doors:
            if door.is_exit and door.locked:
                door.locked = False
                spawn_particles(door.centerx, door.centery, config.C_GOLD, 20, 5)

def append_tiles(map_code, tile):
    if map_code < 0:
        background_tiles.append(tile)
    else:
        tiles.append(tile)

def create_map(stage_map=None):
    global boss
    if stage_map is None:
        stage_map = tile_map.GAME_STAGES.get(current_stage_num, tile_map.STAGE_1_MAP)

    for column in range(len(stage_map[0])):
        for row in range(len(stage_map)):
            map_code = stage_map[row][column]
            x = column * config.TILE_SIZE
            y = row * config.TILE_SIZE
            if map_code == 0:
                continue
            elif abs(map_code) == 1:
                append_tiles(map_code, Tile(x, y, assets.rock_tile1_image))
            elif abs(map_code) == 2:
                append_tiles(map_code, Tile(x, y, assets.rock_tile2_image))
            elif abs(map_code) == 3:
                append_tiles(map_code, Tile(x, y, assets.rock_tile3_image))
            elif abs(map_code) == 4:
                append_tiles(map_code, Tile(x, y, assets.rock_tile4_image))
            elif abs(map_code) == 5:
                append_tiles(map_code, Tile(x, y, assets.floor_tile_image))
            elif abs(map_code) == 6:
                append_tiles(map_code, Tile(x, y, assets.wall_tile_image))
            elif map_code == 7:
                background_tiles.append(Tile(x, y, assets.beam_tile_image))
            elif map_code == 8:
                spikes.append(Tile(x, y, assets.spike_image))
            elif map_code == 9:
                background_tiles.append(Tile(x, y, assets.door_tile_image))
            elif map_code == 10:
                background_tiles.append(Tile(x, y, assets.room_tile_image))
            elif map_code == 11:
                metalls.append(Metall(x, y))
            elif map_code == 12:
                bladers.append(Blader(x, y))

    if current_stage_num == 1:
        checkpoints.append(Checkpoint(config.TILE_SIZE * 3, config.TILE_SIZE * 12))
        keys.append(KeyItem(config.TILE_SIZE * 25, config.TILE_SIZE * 10))
        doors.append(LockedDoor(config.TILE_SIZE * 40, config.TILE_SIZE * 12, is_exit=False))
        doors.append(LockedDoor(config.TILE_SIZE * 201, config.TILE_SIZE * 10, is_exit=True))
        friendly_npcs.append(FriendlyNPC(config.TILE_SIZE * 5, config.TILE_SIZE * 11, "Elder",
            ["Welcome, traveler! The grassland corridor leads to cavern depths.",
             "Defeat 70% of enemies to unlock the EXIT door!",
             "Use the Golden Key for locked gates along the way."]))
        add_quest(Quest("Grassland Patrol", "Defeat 70% of enemies to unlock exit", "kill", 5, 50))
        add_quest(Quest("Key Seeker", "Find the golden key", "collect", 1, 100))
        add_quest(Quest("Door Buster", "Reach the exit door", "reach", 1, 150))

    elif current_stage_num == 2:
        checkpoints.append(Checkpoint(config.TILE_SIZE * 3, config.TILE_SIZE * 12))
        keys.append(KeyItem(config.TILE_SIZE * 20, config.TILE_SIZE * 8))
        doors.append(LockedDoor(config.TILE_SIZE * 96, config.TILE_SIZE * 12, is_exit=True))
        friendly_npcs.append(FriendlyNPC(config.TILE_SIZE * 5, config.TILE_SIZE * 11, "Scout",
            ["You made it to the Cavern!",
             "Watch out for flying Bladers and spike pits.",
             "Find the Golden Key to reach the Boss Fortress!"]))
        add_quest(Quest("Cavern Survival", "Find key & reach Stage 3 exit", "collect", 1, 150))

    elif current_stage_num == 3:
        checkpoints.append(Checkpoint(config.TILE_SIZE * 3, config.TILE_SIZE * 12))
        boss = BossEnemy(config.TILE_SIZE * 25, config.TILE_SIZE * 10)
        doors.append(LockedDoor(config.TILE_SIZE * 36, config.TILE_SIZE * 12, is_exit=True))
        add_quest(Quest("Final Boss", "Defeat the 3-Phase Boss", "kill", 1, 300))

def load_stage(stage_num):
    global current_stage_num, player, metalls, metall_bullets, tiles, background_tiles
    global items, spikes, bladers, particles, checkpoints, last_checkpoint, keys, doors
    global friendly_npcs, current_dialogue, dialogue_timer, boss, inventory
    global show_inventory, active_quests, completed_quests
    global stage_banner_timer, stage_banner_text
    global stage_total_enemies, stage_enemies_killed

    if stage_num > max_stages:
        stage_banner_text = "VICTORY! ALL STAGES CLEARED!"
        stage_banner_timer = pygame.time.get_ticks()
        return

    current_stage_num = stage_num
    metalls.clear()
    metall_bullets.clear()
    tiles.clear()
    background_tiles.clear()
    items.clear()
    spikes.clear()
    bladers.clear()
    particles.clear()
    checkpoints.clear()
    last_checkpoint = None
    keys.clear()
    doors.clear()
    friendly_npcs.clear()
    current_dialogue = None
    dialogue_timer = 0
    boss = None
    stage_enemies_killed = 0

    player.x = config.TILE_SIZE * 2
    player.y = config.TILE_SIZE * 10
    player.velocity_y = 0
    player.jumping = False

    stage_map = tile_map.GAME_STAGES.get(current_stage_num, tile_map.STAGE_1_MAP)
    create_map(stage_map)

    stage_total_enemies = len(metalls) + len(bladers)
    if boss:
        stage_total_enemies += 1

    stage_banner_text = f"ENTERED {STAGE_NAMES.get(current_stage_num, 'New Stage')}"
    stage_banner_timer = pygame.time.get_ticks()

    spawn_particles(player.centerx, player.centery, config.C_GOLD, 30, 6)

def reset_game():
    global current_stage_num, game_over
    current_stage_num = 1
    load_stage(1)
    game_over = False

def check_tile_collision(character):
    for tile in tiles:
        if character.colliderect(tile):
            return tile
        elif tile.x - character.x > config.GAME_WIDTH:
            return None
    return None

def check_tile_collision_x(character):
    tile = check_tile_collision(character)
    if tile is not None:
        if character.velocity_x < 0:
            character.x = tile.x + tile.width
        elif character.velocity_x > 0:
            character.x = tile.x - character.width
        character.velocity_x = 0

def check_tile_collision_y(character):
    tile = check_tile_collision(character)
    if tile is not None:
        if character.velocity_y < 0:
            character.y = tile.y + tile.height
        elif character.velocity_y > 0:
            character.y = tile.y - character.height
            character.jumping = False
        character.velocity_y = 0

def move_map_x(velocity_x):
    for tile in background_tiles:
        tile.x += velocity_x
    for tile in tiles:
        tile.x += velocity_x
    for metall in metalls:
        metall.x += velocity_x
        metall.patrol_start_x += velocity_x
        for bullet in metall.bullets:
            bullet.x += velocity_x
    for bullet in metall_bullets:
        bullet.x += velocity_x
    for item in items:
        item.x += velocity_x
    for spike in spikes:
        spike.x += velocity_x
    for blader in bladers:
        blader.start_x += velocity_x
        blader.x += velocity_x
    for cp in checkpoints:
        cp.x += velocity_x
    for key in keys:
        key.x += velocity_x
    for door in doors:
        door.x += velocity_x
    for npc in friendly_npcs:
        npc.x += velocity_x
    if boss:
        boss.x += velocity_x
        boss.patrol_start_x += velocity_x

def move_player_x(velocity_x):
    move_map_x(velocity_x)
    tile = check_tile_collision(player)
    if tile is not None:
        move_map_x(-velocity_x)

def drop_item(character):
    random_number = random.randint(1, 100)
    if 0 < random_number <= 20:
        items.append(Item(character.x, character.y, assets.big_life_energy_image))
    elif 20 < random_number <= 50:
        items.append(Item(character.x, character.y, assets.life_energy_image))
    elif 50 < random_number <= 75:
        items.append(Item(character.x, character.y, assets.score_ball_image))

def move():
    global metalls, items, bladers, metall_bullets, game_over, last_checkpoint
    global current_dialogue, dialogue_timer, boss
    global stage_enemies_killed

    player.velocity_y += config.GRAVITY
    player.y += player.velocity_y
    check_tile_collision_y(player)

    for spike in spikes:
        if player.colliderect(spike):
            player.health = 0

    for cp in checkpoints:
        if player.colliderect(cp) and not cp.activated:
            cp.activated = True
            last_checkpoint = (cp.x, cp.y)
            spawn_particles(cp.centerx, cp.centery, (100, 255, 100), 15, 4)

    for key in keys:
        if not key.collected and player.colliderect(key):
            key.collected = True
            inventory.add("Golden Key")
            player.keys_found += 1
            spawn_particles(key.x + 10, key.y + 10, config.C_GOLD, 12, 4)
            update_quests("collect")

    for door in doors:
        if door.locked and player.colliderect(door):
            if not door.is_exit and inventory.has("Golden Key"):
                door.locked = False
                inventory.remove("Golden Key")
                spawn_particles(door.centerx, door.centery, config.C_GOLD, 20, 5)
                update_quests("reach")
            else:
                if player.centerx < door.centerx:
                    player.x = door.x - player.width - 2
                else:
                    player.x = door.x + door.width + 2
        elif not door.locked and player.colliderect(door):
            if hasattr(door, 'is_exit') and door.is_exit:
                load_stage(current_stage_num + 1)
                break

    for npc in friendly_npcs:
        if player.colliderect(npc):
            npc.talked = True

    for bullet in player.bullets:
        bullet.x += bullet.velocity_x
        for metall in metalls:
            if metall.health > 0 and not bullet.used and bullet.colliderect(metall):
                bullet.used = True
                if metall.state == config.NPCState.GUARD:
                    spawn_particles(metall.centerx, metall.centery, (200, 200, 200), 4, 2)
                    metall.transition_to(config.NPCState.ATTACK)
                elif not metall.invincible:
                    metall.take_damage(player.damage)
                    spawn_particles(metall.centerx, metall.centery, (255, 100, 0), 6, 3)
                    if metall.health <= 0:
                        drop_item(metall)
                        metall_bullets.extend(metall.bullets)
                        player.gain_xp(config.XP_PER_KILL)
                        update_quests("kill")
                        stage_enemies_killed += 1
                        check_exit_door_unlock()
        for blader in bladers:
            if blader.health > 0 and not bullet.used and bullet.colliderect(blader):
                bullet.used = True
                if not blader.invincible:
                    blader.take_damage(player.damage)
                    spawn_particles(blader.centerx, blader.centery, (255, 100, 0), 6, 3)
                    if blader.health <= 0:
                        drop_item(blader)
                        player.gain_xp(config.XP_PER_KILL)
                        update_quests("kill")
                        stage_enemies_killed += 1
                        check_exit_door_unlock()
        if boss and boss.health > 0 and not bullet.used and bullet.colliderect(boss):
            bullet.used = True
            if getattr(boss, 'guarding', False):
                spawn_particles(boss.centerx, boss.centery, (100, 200, 255), 8, 4)
                boss.counter_attack()
            elif not boss.invincible:
                boss.take_damage(player.damage)
                spawn_particles(boss.centerx, boss.centery, (255, 50, 50), 10, 4)
                if boss.health <= 0:
                    player.gain_xp(200)
                    spawn_particles(boss.centerx, boss.centery, config.C_GOLD, 30, 6)
                    for _ in range(3):
                        items.append(Item(boss.x + random.randint(0, 40), boss.y, assets.big_life_energy_image))
                    update_quests("kill")
                    stage_enemies_killed += 1
                    check_exit_door_unlock()

    player.bullets = [b for b in player.bullets if not b.used
                      and b.x + b.width > 0 and b.x < config.GAME_WIDTH]
    metalls[:] = [m for m in metalls if m.health > 0]
    bladers[:] = [b for b in bladers if b.health > 0]

    for metall in metalls:
        metall.update_ai(player, tiles, metalls)
        metall.update_image()
        metall.update_invincibility()
        metall.velocity_y += config.GRAVITY
        metall.y += metall.velocity_y
        check_tile_collision_y(metall)
        if not player.invincible and player.colliderect(metall):
            player.health -= 1
            player.set_invincible()
            spawn_particles(player.centerx, player.centery, (255, 0, 0), 8, 3)
            if metall.npc_type == config.NPCType.AGGRESSIVE:
                metall.transition_to(config.NPCState.ATTACK)
        for bullet in metall.bullets:
            bullet.x += bullet.velocity_x
            bullet.y += bullet.velocity_y
            if not player.invincible and player.colliderect(bullet):
                player.health -= 2
                bullet.used = True
                player.set_invincible()
                spawn_particles(player.centerx, player.centery, (255, 0, 0), 6, 2)
        metall.bullets = [b for b in metall.bullets if not b.used
                          and b.x + b.width > 0 and b.x < config.GAME_WIDTH]

    for bullet in metall_bullets:
        bullet.x += bullet.velocity_x
        bullet.y += bullet.velocity_y
        if not player.invincible and player.colliderect(bullet):
            player.health -= 2
            bullet.used = True
            player.set_invincible()
            spawn_particles(player.centerx, player.centery, (255, 0, 0), 6, 2)
    metall_bullets[:] = [b for b in metall_bullets if not b.used
                          and b.x + b.width > 0 and b.x < config.GAME_WIDTH]

    for blader in bladers:
        blader.update_ai(player, tiles, bladers)
        blader.update_image()
        blader.update_invincibility()
        if not player.invincible and player.colliderect(blader):
            player.health -= 1
            player.set_invincible()
            spawn_particles(player.centerx, player.centery, (255, 0, 0), 8, 3)

    if boss and boss.health > 0:
        boss.update_ai(player, tiles, [])
        boss.update_invincibility()

        # Apply gravity if not hovering in Phase 2 or airborne during slam attack
        if not getattr(boss, 'flying', False) and not getattr(boss, 'is_slimming', False):
            if not hasattr(boss, 'velocity_y'):
                boss.velocity_y = 0
            boss.velocity_y += config.GRAVITY
            boss.y += boss.velocity_y
            check_tile_collision_y(boss)

        # Process minion spawn requests
        while getattr(boss, 'minions_to_spawn', []):
            m_type, mx, my = boss.minions_to_spawn.pop(0)
            if m_type == 'metall':
                metalls.append(Metall(mx, my))
            elif m_type == 'blader':
                bladers.append(Blader(mx, my))

        if not player.invincible and player.colliderect(boss):
            player.health -= 3
            player.set_invincible()
            spawn_particles(player.centerx, player.centery, (255, 0, 0), 10, 4)
        for bullet in boss.bullets:
            bullet.x += bullet.velocity_x
            bullet.y += bullet.velocity_y
            if not player.invincible and player.colliderect(bullet):
                player.health -= 2
                bullet.used = True
                player.set_invincible()
                spawn_particles(player.centerx, player.centery, (255, 0, 0), 6, 2)
        boss.bullets = [b for b in boss.bullets if not b.used
                        and b.x + b.width > 0 and b.x < config.GAME_WIDTH]

    for item in items:
        item.velocity_y += config.GRAVITY
        item.y += item.velocity_y
        check_tile_collision_y(item)
        if player.colliderect(item):
            item.used = True
            if item.image == assets.life_energy_image:
                player.health = min(player.health + 2, player.max_health)
                spawn_particles(item.centerx, item.centery, (0, 255, 100), 8, 2)
            elif item.image == assets.big_life_energy_image:
                player.health = min(player.health + 8, player.max_health)
                spawn_particles(item.centerx, item.centery, (0, 255, 100), 12, 3)
            elif item.image == assets.score_ball_image:
                player.score += 1000
                spawn_particles(item.centerx, item.centery, config.C_GOLD, 10, 3)
    items[:] = [it for it in items if not it.used]

    for p in particles:
        p.update()
    particles[:] = [p for p in particles if p.alive]

    if player.health <= 0 or player.y > config.GAME_HEIGHT:
        if last_checkpoint:
            player.health = player.max_health
            player.x = last_checkpoint[0]
            player.y = last_checkpoint[1] - config.TILE_SIZE
            player.velocity_y = 0
            spawn_particles(player.centerx, player.centery, (100, 255, 100), 15, 4)
        else:
            game_over = True

def draw(window):
    window.fill((20, 18, 167))
    window.blit(assets.background_image, (0, 80))

    camera_x = 0

    for tile in background_tiles:
        if tile.x > config.GAME_WIDTH:
            break
        window.blit(tile.image, tile)

    for tile in tiles:
        if tile.x > config.GAME_WIDTH:
            break
        window.blit(tile.image, tile)

    for spike in spikes:
        if spike.x > config.GAME_WIDTH:
            break
        window.blit(spike.image, spike)

    for cp in checkpoints:
        if cp.x > config.GAME_WIDTH + config.TILE_SIZE or cp.x < -config.TILE_SIZE:
            continue
        cp.draw(window, camera_x)

    for key in keys:
        if key.x > config.GAME_WIDTH + config.TILE_SIZE or key.x < -config.TILE_SIZE:
            continue
        key.draw(window, camera_x)

    for door in doors:
        if door.x > config.GAME_WIDTH + config.TILE_SIZE or door.x < -config.TILE_SIZE:
            continue
        door.draw(window, camera_x)

    for npc in friendly_npcs:
        if npc.x > config.GAME_WIDTH + config.TILE_SIZE or npc.x < -config.TILE_SIZE:
            continue
        npc.draw(window, camera_x)

    player.update_image()
    window.blit(player.image, player)

    for bullet in player.bullets:
        window.blit(bullet.image, bullet)

    for metall in metalls:
        if metall.x <= config.GAME_WIDTH and metall.x > -config.TILE_SIZE:
            if metall.invincible and (pygame.time.get_ticks() // 80) % 2 == 0:
                pass
            else:
                window.blit(metall.image, metall)
            metall.draw_ai_overlay(window, camera_x)
        for bullet in metall.bullets:
            window.blit(bullet.image, bullet)

    for bullet in metall_bullets:
        window.blit(bullet.image, bullet)

    for blader in bladers:
        if blader.x > config.GAME_WIDTH + config.TILE_SIZE or blader.x < -config.TILE_SIZE:
            continue
        blader.update_image()
        if blader.invincible and (pygame.time.get_ticks() // 80) % 2 == 0:
            pass
        else:
            window.blit(blader.image, blader)
        blader.draw_ai_overlay(window, camera_x)

    if boss and boss.health > 0:
        if boss.x <= config.GAME_WIDTH and boss.x > -config.TILE_SIZE:
            boss.draw(window, camera_x)

    for item in items:
        if item.x > config.GAME_WIDTH + config.TILE_SIZE or item.x < -config.TILE_SIZE:
            continue
        window.blit(item.image, item)

    for p in particles:
        p.draw(window, camera_x)

    # Health Bar
    pygame.draw.rect(window, (0, 0, 0), (config.TILE_SIZE, config.TILE_SIZE, config.HEALTH_WIDTH, config.HEALTH_HEIGHT * player.max_health))
    for i in range(player.max_health - player.health, player.max_health):
        window.blit(assets.health_image, (config.TILE_SIZE, config.TILE_SIZE + i * config.HEALTH_HEIGHT, config.HEALTH_WIDTH, config.HEALTH_HEIGHT))

    # XP Bar
    xp_bar_w = 200
    xp_bar_h = 8
    xp_pct = min(1.0, player.xp / player.xp_to_next) if player.xp_to_next > 0 else 0
    pygame.draw.rect(window, (40, 40, 60), (config.GAME_WIDTH // 2 - xp_bar_w // 2, 8, xp_bar_w, xp_bar_h))
    pygame.draw.rect(window, config.C_XP, (config.GAME_WIDTH // 2 - xp_bar_w // 2, 8, int(xp_bar_w * xp_pct), xp_bar_h))
    pygame.draw.rect(window, (100, 100, 150), (config.GAME_WIDTH // 2 - xp_bar_w // 2, 8, xp_bar_w, xp_bar_h), 1)
    lvl_txt = small_font.render(f"LVL {player.level}", True, config.C_TEXT)
    window.blit(lvl_txt, (config.GAME_WIDTH // 2 - xp_bar_w // 2 - 50, 6))

    # Stage Header
    stg_name = STAGE_NAMES.get(current_stage_num, f"Stage {current_stage_num}")
    stg_text = small_font.render(f"Stage {current_stage_num}/{max_stages}: {stg_name}", True, config.C_GOLD)
    window.blit(stg_text, (config.TILE_SIZE + 25, 8))

    # Stage Banner Overlay
    if stage_banner_text and pygame.time.get_ticks() - stage_banner_timer < 3000:
        b_w = 420
        b_h = 50
        b_x = config.GAME_WIDTH // 2 - b_w // 2
        b_y = config.GAME_HEIGHT // 3
        s = pygame.Surface((b_w, b_h), pygame.SRCALPHA)
        s.fill((20, 20, 40, 220))
        window.blit(s, (b_x, b_y))
        pygame.draw.rect(window, config.C_GOLD, (b_x, b_y, b_w, b_h), 2)
        b_surf = game_font.render(stage_banner_text, True, config.C_GOLD)
        window.blit(b_surf, (b_x + (b_w - b_surf.get_width()) // 2, b_y + 10))

    # Score
    text_score = str(player.score).zfill(7)
    text_surface = game_font.render(text_score, False, "white")
    window.blit(text_surface, (config.GAME_WIDTH / 2, config.TILE_SIZE / 2 + 12))

    # Keys
    if player.keys_found > 0:
        key_txt = small_font.render(f"Keys: {player.keys_found}", True, config.C_GOLD)
        window.blit(key_txt, (config.GAME_WIDTH - 100, 10))

    # Quest Tracker
    quest_y = 40
    for quest in active_quests:
        if not quest.completed:
            color = (200, 200, 100)
            q_text = f"[!] {quest.title}: {quest.current_count}/{quest.target_count}"
        else:
            color = (100, 255, 100)
            q_text = f"[Done] {quest.title}"
        q_surf = small_font.render(q_text, True, color)
        window.blit(q_surf, (config.GAME_WIDTH - q_surf.get_width() - 10, quest_y))
        quest_y += 18

    # State Legend
    legend_y = config.GAME_HEIGHT - 30
    legend_x = 10
    legend_text = small_font.render("NPC States:", True, (180, 180, 180))
    window.blit(legend_text, (legend_x, legend_y - 14))
    for state, color in config.STATE_COLORS.items():
        pygame.draw.circle(window, color, (legend_x + 8, legend_y + 4), 4)
        legend_x += 18

    # Kill Progress Bar
    killed, total, pct = get_kill_progress()
    req_kills = math.ceil(total * KILL_REQUIREMENT_PCT)
    bar_w = 160
    bar_h = 12
    bar_x = config.GAME_WIDTH - bar_w - 10
    bar_y = config.GAME_HEIGHT - 42
    pygame.draw.rect(window, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h))
    fill_color = (50, 200, 80) if pct >= KILL_REQUIREMENT_PCT else (200, 80, 50)
    pygame.draw.rect(window, fill_color, (bar_x, bar_y, int(bar_w * min(1.0, pct)), bar_h))
    marker_x = bar_x + int(bar_w * KILL_REQUIREMENT_PCT)
    pygame.draw.line(window, config.C_GOLD, (marker_x, bar_y - 2), (marker_x, bar_y + bar_h + 2), 2)
    pygame.draw.rect(window, (150, 150, 200), (bar_x, bar_y, bar_w, bar_h), 1)
    kill_label = small_font.render(f"Defeated: {killed}/{total} (need {req_kills})", True, config.C_TEXT)
    window.blit(kill_label, (bar_x, bar_y - 16))
    if pct >= KILL_REQUIREMENT_PCT:
        unlock_txt = small_font.render("EXIT UNLOCKED!", True, (50, 255, 80))
        window.blit(unlock_txt, (bar_x, bar_y + bar_h + 2))
    count_text = small_font.render(f"Alive: {len(metalls) + len(bladers)}  Boss: {'Alive' if boss and boss.health > 0 else 'N/A' if not boss else 'Dead'}", True, (255, 255, 255))
    window.blit(count_text, (bar_x, config.GAME_HEIGHT - 14))

    # Dialogue Box
    if current_dialogue:
        name, text, _ = current_dialogue
        box_h = 60
        pygame.draw.rect(window, (20, 20, 40), (20, config.GAME_HEIGHT - box_h - 20, config.GAME_WIDTH - 40, box_h))
        pygame.draw.rect(window, (150, 150, 200), (20, config.GAME_HEIGHT - box_h - 20, config.GAME_WIDTH - 40, box_h), 2)
        name_surf = small_font.render(name, True, config.C_GOLD)
        window.blit(name_surf, (30, config.GAME_HEIGHT - box_h - 14))
        text_surf = dialogue_font.render(text, True, config.C_TEXT)
        window.blit(text_surf, (30, config.GAME_HEIGHT - box_h + 10))

    # Inventory Overlay
    if show_inventory:
        inv_w = 200
        inv_h = 250
        inv_x = config.GAME_WIDTH // 2 - inv_w // 2
        inv_y = config.GAME_HEIGHT // 2 - inv_h // 2
        s = pygame.Surface((inv_w, inv_h), pygame.SRCALPHA)
        s.fill((20, 20, 40, 220))
        window.blit(s, (inv_x, inv_y))
        pygame.draw.rect(window, (150, 150, 200), (inv_x, inv_y, inv_w, inv_h), 2)
        title = game_font.render("Inventory", True, config.C_GOLD)
        window.blit(title, (inv_x + 10, inv_y + 10))
        iy = inv_y + 50
        for item_name, count in inventory.items.items():
            line = small_font.render(f"{item_name} x{count}", True, config.C_TEXT)
            window.blit(line, (inv_x + 15, iy))
            iy += 22
        hint = small_font.render("Press [1-8] to use item", True, (150, 150, 150))
        window.blit(hint, (inv_x + 10, inv_y + inv_h - 25))

    # Game Over
    if game_over:
        overlay = pygame.Surface((config.GAME_WIDTH, config.GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        window.blit(overlay, (0, 0))
        text_surface = game_font.render("Game Over", False, (255, 80, 80))
        window.blit(text_surface, (config.GAME_WIDTH / 8, config.GAME_HEIGHT / 2))
        text_surface = game_font.render("Press [Enter] to Restart", False, "white")
        window.blit(text_surface, (config.GAME_WIDTH / 8, config.GAME_HEIGHT / 2 + config.TILE_SIZE))
