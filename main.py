"""
Main Game Entry Point
=====================
Initializes Pygame, configures display window, manages event loop,
and drives frame updates for the Adventure Platformer game.
"""
# pyrefly: ignore [missing-import]
import pygame
import sys
import config
import assets
import game_manager
from particles import spawn_particles

def main():
    pygame.init()
    pygame.font.init()

    window = pygame.display.set_mode((config.GAME_WIDTH, config.GAME_HEIGHT))
    pygame.display.set_caption("Adventure Platformer - Intelligent NPCs & FSM Engine")
    pygame.display.set_icon(assets.player_image_right)
    clock = pygame.time.Clock()

    # Load initial stage 1
    game_manager.load_stage(1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == config.INVINCIBLE_END:
                game_manager.player.invincible = False
            elif event.type == config.SHOOTING_END:
                game_manager.player.shooting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    game_manager.show_inventory = not game_manager.show_inventory
                elif event.key == pygame.K_1 and game_manager.show_inventory:
                    game_manager.inventory.use("Health Potion", game_manager.player)
                elif event.key == pygame.K_e:
                    for npc in game_manager.friendly_npcs:
                        if game_manager.player.colliderect(npc):
                            text = npc.get_dialogue()
                            game_manager.current_dialogue = (npc.name, text, pygame.time.get_ticks())
                            game_manager.dialogue_timer = pygame.time.get_ticks()

        if game_manager.current_dialogue and pygame.time.get_ticks() - game_manager.current_dialogue[2] > 4000:
            game_manager.current_dialogue = None

        keys_pressed = pygame.key.get_pressed()

        if (keys_pressed[pygame.K_RETURN] or keys_pressed[pygame.K_KP_ENTER]) and game_manager.game_over:
            game_manager.reset_game()

        if not game_manager.game_over:
            if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and not game_manager.player.jumping:
                game_manager.player.velocity_y = config.PLAYER_VELOCITY_Y
                game_manager.player.jumping = True
                spawn_particles(game_manager.player.centerx, game_manager.player.bottom, (200, 200, 200), 4, 2)

            if (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a] or
                keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]):
                game_manager.player.walking = True
            else:
                game_manager.player.walking = False

            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                game_manager.move_player_x(config.PLAYER_VELOCITY_X)
                game_manager.player.direction = "left"

            if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                game_manager.move_player_x(-config.PLAYER_VELOCITY_X)
                game_manager.player.direction = "right"

            if keys_pressed[pygame.K_x] or keys_pressed[pygame.K_SPACE]:
                game_manager.player.set_shooting()

            game_manager.move()

        game_manager.draw(window)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
