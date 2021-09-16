import pygame
import sys

import scripts.ui_elements.font_enhanced as font

clock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('font_test')
screen = pygame.display.set_mode((800, 400),0,32)

my_font = font.Font('assets/fonts/small_font.png', (255, 255, 255))
my_big_font = font.Font('assets/fonts/large_font.png', (255, 255, 255))
my_red_font = font.Font('assets/fonts/small_font.png', (255, 0, 0))
my_str = 'abcdef<!1>gh<!0>i<!1>j<!0>klmnop qrstuvwxyz<!2>ABCDEF Hello W<!0>orld!\n\nbapjs odhao<!1>ishdoi ahoidhaoin aisdiahs asdio<!0>haph adsiahspahd aisohdoiahd\n\ndhaihdaiuhdw adhoaihdhaioiohasdiaoh'
my_str += '\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. <!1>Ut enim<!0> ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
my_text = font.formatted_text_gen(my_str, my_font, my_red_font, my_big_font, max_width=200)
my_text.adjust_scale(30, 50, 1.4)

i = -20
j = 0

while True:

    screen.fill((0,0,0))
    mx, my = pygame.mouse.get_pos()
    #draw_line((mx, my), (100, 100))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(100, 100, 204, 800), width=1)
    my_text.render(screen, (102, 100))
    my_text.visible_range = [int(i), j]
    i += 0.5
    j += 1
    if i > my_text.length + 30:
        i = -20
        j = 0

    # fades text in
    my_text.adjust_scale(j - 20, j - 16, 1)
    my_text.adjust_scale(j - 12, j, 0.8)
    my_text.adjust_alpha(j - 20, j - 16, 255)
    my_text.adjust_alpha(j - 16, j - 8, 100)
    my_text.adjust_alpha(j - 8, j, 40)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_e:
                print(j)

    pygame.display.update()
    clock.tick(60)
