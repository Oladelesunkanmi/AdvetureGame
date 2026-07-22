import pygame
from sys import exit #termiate the program

GAME_WIDTH = 512
GAME_HEIGHT = 512
pygame.init() #always initialize pygame before using it
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT   )) #create a window of size 512x512     
pygame.display.set_caption("Game Window") #title of the window
clock = pygame.time.Clock() #create a clock object to control the frame rate

player = pygame.Rect(100, 100, 50, 50) #create a rectangle to represent the player  

def draw():
    window.fill((50, 40, 50)) #fill the window with grey color
    pygame.draw.rect(window, (255, 0, 0), player) #draw the player rectangle

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # if event.type == pygame.KEYDOWN:
        #     if event.key in (pygame.K_UP, pygame.K_w):
        #         player.y -= 5
        #     elif event.key in (pygame.K_DOWN, pygame.K_s):
        #         player.y += 5
        #     elif event.key in (pygame.K_LEFT, pygame.K_a):
        #         player.x -= 5
        #     elif event.key in (pygame.K_RIGHT, pygame.K_d):
        #         player.x += 5
        keys = pygame.key.get_pressed() #get the state of all keyboard keys
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += 5   
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += 5


    draw()
    pygame.display.update()
    clock.tick(60) #limit the frame rate to 60 frames per second

    