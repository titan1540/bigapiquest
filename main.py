import os
import sys
import requests
import pygame

import mapapi
import geocoder

pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 620, 510
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
INCLUDED_SYMBOLS = ' ,.-()/\\'

all_sprites = pygame.sprite.Group()
borders = pygame.sprite.Group()
buttons = pygame.sprite.Group()


class Border(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__(all_sprites, borders)
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.image = pygame.Surface((width, height),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('black'),
                         (0, 0, width, height), 1)


class InputLabel(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__(all_sprites)
        self.font = pygame.font.Font(None, 30)
        self.request = ''
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.image = self.font.render(self.request, 1, pygame.Color('black'))

    def push_button(self, event):
        global INCLUDED_SYMBOLS
        if event.key == pygame.K_BACKSPACE:
            self.request = self.request[:-1]
        else:
            if event.unicode.isalnum() or event.unicode in INCLUDED_SYMBOLS:
                self.request += event.unicode
        self.image = self.font.render(self.request, 1, pygame.Color('black'))

    def get_text(self):
        return self.request


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height, text, action):
        super().__init__(all_sprites, buttons)
        self.action = action
        self.font = pygame.font.Font(None, 30)
        self.request = text
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.image = self.font.render(self.request, 1, pygame.Color('black'))

    def update(self, event):
        if self.rect.x < event.pos[0] < self.rect.x + self.rect.width and \
                self.rect.y < event.pos[1] < self.rect.y + self.rect.height:
            self.action()


class MapImage(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(10, 50, 600, 450)
        self.image = pygame.Surface((600, 450),
                                    pygame.SRCALPHA, 32)
        self.spn = None
        self.ll = None

    def update_map(self, event=None):
        if event is not None:
            if event.key == pygame.K_PAGEUP:
                if self.spn[0] * 2 <= 90 and self.spn[1] * 2 <= 90:
                    self.spn = self.spn[0] * 2, self.spn[1] * 2
            else:
                if self.spn[0] / 2 >= 0.001 and self.spn[1] / 2 >= 0.001:
                    self.spn = self.spn[0] / 2, self.spn[1] / 2
            mapapi.save_map(self.ll, self.spn)

        self.image = load_image('_map.png')

    def new_map(self):
        coordinates = input_label[0].get_text()
        toponym = geocoder.get_toponym(coordinates)
        self.spn = geocoder.get_spn(toponym)
        self.ll = geocoder.get_ll(toponym)
        mapapi.save_map(self.ll, self.spn)
        self.update_map()


input_label = (InputLabel(15, 15, 100, 20), Border(10, 10, 300, 30))

map_img = (MapImage(), Border(10, 50, 600, 450))
btn_search = (Button(330, 15, 100, 20, 'Найти', map_img[0].new_map), Border(320, 10, 80, 30))


def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


running = True

while running:
    screen.fill(pygame.Color('white'))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_PAGEUP or event.key == pygame.K_PAGEDOWN):
            map_img[0].update_map(event)
        elif event.type == pygame.KEYDOWN:
            input_label[0].push_button(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            buttons.update(event)

    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
try:
    os.remove('_map.png')
except:
    pass
