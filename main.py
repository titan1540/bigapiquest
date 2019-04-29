import os
import pygame

import mapapi
import geocoder
import searchapi

pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 730, 550
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
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.font = pygame.font.Font(None, 25)
        self.request = ''
        self.rect = pygame.Rect(pos_x, pos_y, 0, 0)
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


class TextLabel(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.font = pygame.font.Font(None, 15)
        self.text = ''
        self.rect = pygame.Rect(pos_x, pos_y, 0, 0)
        self.image = self.font.render(self.text, 1, pygame.Color('black'))

    def set_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, 1, pygame.Color('black'))


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
            self.action(event)


class MapImage(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(10, 90, 600, 450)
        self.image = pygame.Surface((600, 450),
                                    pygame.SRCALPHA, 32)
        self.spn = None
        self.ll = None
        self.map_type = 'map'
        self.pt = None
        self.address = None
        self.postcode = 1

    def new_map(self, request):
        try:
            toponym = geocoder.get_toponym(request)
        except:
            font = pygame.font.Font(None, 50)
            self.image = font.render('Введите корректные координаты', 1, pygame.Color('red'))
            return
        self.spn = geocoder.get_spn(toponym)
        self.ll = geocoder.get_ll(toponym)
        self.pt = self.ll
        self.address = geocoder.get_address(toponym)
        self.update_map()

    def update_spn(self, event):
        if event.key == pygame.K_PAGEUP:
            if self.spn[0] * 2 <= 90 and self.spn[1] * 2 <= 90:
                self.spn = self.spn[0] * 2, self.spn[1] * 2
        else:
            if self.spn[0] / 2 >= 0.001 and self.spn[1] / 2 >= 0.001:
                self.spn = self.spn[0] / 2, self.spn[1] / 2
        self.update_map()

    def update_map(self):
        mapapi.save_map(self.ll, self.spn, self.map_type, point=self.pt)
        self.image = load_image('_map.png')

    def move_map(self, event):
        if event.key == pygame.K_RIGHT:
            if self.ll[0] + self.spn[0] / 3 < 180:
                self.ll = self.ll[0] + self.spn[0] / 3, self.ll[1]
        if event.key == pygame.K_LEFT:
            if self.ll[0] - self.spn[0] / 3 > -180:
                self.ll = self.ll[0] - self.spn[0] / 3, self.ll[1]
        if event.key == pygame.K_UP:
            if self.ll[1] + self.spn[1] / 3 < 90:
                self.ll = self.ll[0], self.ll[1] + self.spn[1] / 3
        if event.key == pygame.K_DOWN:
            if self.ll[1] - self.spn[1] / 3 > -90:
                self.ll = self.ll[0], self.ll[1] - self.spn[1] / 3

        self.update_map()

    def update_type(self, map_type):
        self.map_type = map_type
        self.update_map()

    def discard_point(self, event=None):
        self.pt = None
        self.update_map()

    def get_address(self):
        text = self.address[0]
        text += (', ' + self.address[1]) * self.postcode
        return text

    def onoff_postcode(self, event=None):
        self.postcode ^= 1

    def click_left(self, event):
        if 10 <= event.pos[0] <= 610 and 90 <= event.pos[1] <= 540 and self.ll is not None:
            left = self.ll[0] - self.spn[0] / 2
            down = self.ll[1] - self.spn[1] / 2

            dx = (event.pos[0] - 10) / 600
            dy = 1 - (event.pos[1] - 90) / 450

            left += (dx * self.spn[0])
            down += (dy * self.spn[1])

            request = str(left) + ' ' + str(down)

            self.new_map(request)

    def click_right(self, event):
        if 10 <= event.pos[0] <= 610 and 90 <= event.pos[1] <= 540 and self.ll is not None:
            left = self.ll[0] - self.spn[0] / 2
            down = self.ll[1] - self.spn[1] / 2

            dx = (event.pos[0] - 10) / 600
            dy = 1 - (event.pos[1] - 90) / 450

            left += (dx * self.spn[0])
            down += (dy * self.spn[1])

            request = str(left) + ' ' + str(down)

            toponym = geocoder.get_toponym(request)
            organization_coordinates = searchapi.get_nearest_organization(toponym)[1]

            if organization_coordinates is not None:
                self.discard_point(event)
                self.new_map(','.join(str(x) for x in organization_coordinates))



map_img = MapImage()
Border(10, 90, 600, 450)

input_label = InputLabel(15, 15)
Border(10, 10, 510, 30)

address = TextLabel(15, 60)
Border(10, 50, 600, 30)


def search(event=None):
    map_img.new_map(input_label.get_text())
    address.set_text(map_img.get_address())


btn_search = Button(540, 15, 70, 20, 'Найти', search)
Border(530, 10, 80, 30)


def discard(event=None):
    map_img.discard_point()
    address.set_text('')


btn_discard = Button(625, 15, 85, 20, 'Сбросить', discard)
Border(620, 10, 105, 30)


def postcode(event=None):
    map_img.onoff_postcode()
    address.set_text(map_img.get_address())


btn_postcode = Button(625, 55, 70, 20, 'Индекс', postcode)
Border(620, 50, 90, 30)

btn_scheme = Button(625, 95, 85, 20, 'Схема', lambda x: map_img.update_type('map'))
Border(620, 90, 90, 30)
btn_satellite = Button(625, 125, 85, 20, 'Спутник', lambda x: map_img.update_type('sat'))
Border(620, 120, 90, 30)
btn_hybrid = Button(625, 155, 85, 20, 'Гибрид', lambda x: map_img.update_type('sat,skl'))
Border(620, 150, 90, 30)


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
            map_img.update_spn(event)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            btn_search.action(event)
        elif event.type == pygame.KEYDOWN and 273 <= event.key <= 276:
            map_img.move_map(event)
        elif event.type == pygame.KEYDOWN:
            input_label.push_button(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            buttons.update(event)
            map_img.click_left(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            map_img.click_right(event)
            address.set_text(map_img.get_address())

    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
try:
    os.remove('_map.png')
except Exception:
    pass
