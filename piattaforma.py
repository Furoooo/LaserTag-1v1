import pygame
from math import ceil
from utils import scale_image

BG = scale_image(pygame.image.load('imgs/background.png'), 2)

class Piattaforma():
    def __init__(self, display, nomefile = './mappe/game_map.txt') -> None:
        self.display = display
        self.wall_image = pygame.image.load('./imgs/wall.png')
        with open(nomefile) as f:
            self.game_map = [list(map(int, riga.strip().split())) for riga in f]
        self.num_rows = len(self.game_map)
        self.num_cols = len(self.game_map[0])
        self.tile_width = ceil(display.get_width() / self.num_cols)
        self.tile_height = ceil(display.get_height() / self.num_rows)
        self.wall_image = pygame.transform.scale(self.wall_image, (self.tile_width, self.tile_height))

        self.tile_rects = []
        for y, row in enumerate(self.game_map):
            for x, tile in enumerate(row):
                if tile != 0:
                    self.tile_rects.append(pygame.Rect(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height))
    
    def draw(self):
        self.display.fill((146,244,255))
        self.display.blit(BG, (0, 0))
        for y, row in enumerate(self.game_map):
            for x, tile in enumerate(row):
                if tile == 1:
                    self.display.blit(self.wall_image, (x * self.tile_width, y * self.tile_height))