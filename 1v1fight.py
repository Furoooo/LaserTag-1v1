import pygame
from utils import scale_image
from piattaforma import Piattaforma
from varie import *

pygame.init()

SCREEN_LARG = 1200
SCREEN_ALTE = 680

window_size = (SCREEN_LARG, SCREEN_ALTE)
display = pygame.Surface((1200, 680))

screen = pygame.display.set_mode((SCREEN_LARG, SCREEN_ALTE))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
FPS = 60


moving_left = False
moving_right = False
shoot = False

moving_left_1 = False
moving_right_1 = False
moving_up_1 = False
moving_down_1 = False
shoot1 = False

moving_left_2 = False
moving_right_2 = False
moving_up_2 = False
moving_down_2 = False
shoot2 = False

RED = (255, 0, 0)
BLUE = (0, 0 ,255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class giocatore(pygame.sprite.Sprite):
    def __init__(self, display, piattaforma, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.display = display
        self.piattaforma = piattaforma
        
        self.char_type = char_type
        self.speed = speed
        
        self.shoot_cooldown = 0
        self.health = 50
        self.max_health = self.health
        
        self.direction_x = 1
        self.direction_y = 0
        self.flip = False
        
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ['Back', 'Front', 'Side', 'Dead']
        
        for animation in animation_types:
            temp_list = []
            img = pygame.image.load(f'imgs/{self.char_type}/{animation}/0.png').convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.img = img
            temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        self.update_animations()
        self.check_alive()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right, moving_up, moving_down):
        dx = 0
        dy = 0
        
        if moving_left:
            self.direction_x = -1
            self.direction_y = 0 
            dx = -self.speed
            self.flip = True
            
        elif moving_right:
            self.direction_x = 1
            self.direction_y = 0
            dx = self.speed
            self.flip = False

        elif moving_up == True:
            self.direction_y = 1
            self.direction_x = 0
            dy = -self.speed
            self.flip = False
            
        elif moving_down == True:
            self.direction_y = -1
            self.direction_x = 0
            dy = self.speed
            self.flip = False
        

        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}


        hit_list = collision_test(self.rect, self.piattaforma.tile_rects)
        for tile in hit_list:
            # muovo a destra
            if self.rect.centerx <= tile.left and self.rect.right >= tile.left:
                self.rect.right = tile.left - 5
                collision_types['right'] = True
            # muovo a sinistra
            if self.rect.centerx >= tile.right and self.rect.left <= tile.right:
                self.rect.left = tile.right
                collision_types['left'] = True

        for tile in hit_list:
            # muovo in basso
            if self.rect.centery <= tile.top and self.rect.bottom >= tile.top:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            # muovo in alto
            elif self.rect.centery >= tile.bottom and self.rect.top <= tile.bottom:
                self.rect.top = tile.bottom
                collision_types['top'] = True

        # devo controllare anche se esco dallo schermo di lato (potrei inventare un modo con dei rect che formano il bordo)
        if self.rect.left < 0:
            self.rect.left = 0 
        if self.rect.right > self.display.get_width():
            self.rect.right = self.display.get_width()
        if self.rect.top < 0:
            self.rect.top = 0 
        if self.rect.bottom > self.display.get_height():
            self.rect.bottom = self.display.get_height()

        if collision_types['bottom']:
            dy = 0
        if collision_types['top']:
            dy = 0
        if collision_types['left']:
            dx = 0
        if collision_types['right']:
            dx = 0
        
        if dx:
            self.rect.x += dx
        else:
            self.rect.y += dy
    
    def update_animations(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    
    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 30
            if abs(self.direction_x) == 1:
                bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction_x), self.rect.centery, self.direction_x, self.direction_y, display, piattaforma)
            else:
                bullet = Bullet(self.rect.centerx , self.rect.centery - (0.7 * self.rect.size[0] * self.direction_y), self.direction_x, self.direction_y, display, piattaforma)
            bullet_group.add(bullet)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        self.display.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class HealthBar1():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health  = health

        ratio = self.health / self.max_health
        pygame.draw.rect(display, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(display, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(display, GREEN, (self.x, self.y, 150 * ratio, 20))

class HealthBar2():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health  = health

        ratio = self.health / self.max_health
        diff = 150 - (150 * ratio)
        pygame.draw.rect(display, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(display, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(display, GREEN, (self.x + diff, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, display, piattaforma):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = pygame.image.load('imgs/bullet.png').convert_alpha()
        
        self.display = display
        self.piattaforma = piattaforma

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction_x = direction_x
        self.direction_y = direction_y

    def update(self):
        if self.direction_x != 0:
            self.rect.x += (self.direction_x * self.speed)
        elif self.direction_y != 0:
            self.rect.y -= (self.direction_y * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_LARG or self.rect.bottom > SCREEN_ALTE or self.rect.top < 0:
            self.kill()

        if pygame.sprite.spritecollide(player2, bullet_group, False):
            if player2.alive:
                player2.health -= 10
                self.kill()
        
        if pygame.sprite.spritecollide(player1, bullet_group, False):
            if player1.alive:
                player1.health -= 10
                self.kill()


        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        hit_list = collision_test(self.rect, self.piattaforma.tile_rects)
        for tile in hit_list:
            # muovo a destra
            if self.direction_x == 1:
                self.rect.right = tile.left
                collision_types['right'] = True
            # muovo a sinistra
            if self.direction_x == -1:
                self.rect.left = tile.right
                collision_types['left'] = True

        hit_list = collision_test(self.rect, self.piattaforma.tile_rects)
        for tile in hit_list:
            # muovo in basso
            if self.direction_y == -1:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            # muovo in alto
            if self.direction_y == 1:
                self.rect.top = tile.bottom
                collision_types['top'] = True

        # devo controllare anche se esco dallo schermo di lato (potrei inventare un modo con dei rect che formano il bordo)
        if self.rect.left < 0:
            self.rect.left = 0 
        if self.rect.right > self.display.get_width():
            self.rect.right = self.display.get_width()
        if self.rect.top < 0:
            self.rect.top = 0 
        if self.rect.bottom > self.display.get_height():
            self.rect.bottom = self.display.get_height()

        if collision_types['bottom']:
            self.kill()
        if collision_types['top']:
            self.kill()
        if collision_types['left']:
            self.kill()
        if collision_types['right']:
            self.kill()

bullet_group = pygame.sprite.Group()

piattaforma = Piattaforma(display)

player1 = giocatore(display, piattaforma, 'player1', 200, 200, 2, 2)
player2 = giocatore(display, piattaforma, 'player2', 200, 200, 2, 2)
health_bar1 = HealthBar1(10, 10, player1.health, player1.health)
health_bar2 = HealthBar2(1040, 10, player2.health, player2.health)


run = True
while run:

    clock.tick(FPS)

    player1.update()
    player1.draw()
    player2.update()
    player2.draw()
    health_bar1.draw(player1.health)
    health_bar2.draw(player2.health)
    
    piattaforma.draw()
    player1.draw()
    player2.draw()
    health_bar1.draw(player1.health)
    health_bar2.draw(player2.health)
    surf = pygame.transform.scale(display, window_size)
    screen.blit(surf, (0,0))


    bullet_group.update()
    bullet_group.draw(screen)

    if player1.alive and player2.alive:
        if shoot1:
            player1.shoot()
        if moving_left_1 or moving_right_1:
            player1.update_action(2)
        elif moving_down_1:
            player1.update_action(0)
        elif moving_up_1:
            player1.update_action(1)
        player1.move(moving_left_1, moving_right_1, moving_up_1, moving_down_1)

        if shoot2:
            player2.shoot()
        if moving_left_2 or moving_right_2:
                player2.update_action(2)
        elif moving_up_2:
                player2.update_action(1)
        elif moving_down_2:
                player2.update_action(0)
        player2.move(moving_left_2, moving_right_2, moving_up_2, moving_down_2)
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_right_1 = False
                    moving_left_1 = True
                    moving_up_1 = False
                    moving_down_1 = False
                if event.key == pygame.K_d:
                    moving_right_1 = True
                    moving_left_1 = False
                    moving_up_1 = False
                    moving_down_1 = False
                if event.key == pygame.K_w:
                    moving_right_1 = False
                    moving_left_1 = False
                    moving_up_1 = True
                    moving_down_1 = False
                if event.key == pygame.K_s:
                    moving_right_1 = False
                    moving_left_1 = False
                    moving_up_1 = False
                    moving_down_1 = True
                if event.key == pygame.K_SPACE:
                    shoot1 = True
                    

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left_1 = False
                if event.key == pygame.K_d:
                    moving_right_1 = False
                if event.key == pygame.K_w:
                    moving_up_1 = False
                if event.key == pygame.K_s:
                    moving_down_1 = False
                if event.key == pygame.K_SPACE:
                    shoot1 = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j: 
                    moving_left_2 = True
                if event.key == pygame.K_l:
                    moving_right_2 = True
                if event.key == pygame.K_i: 
                    moving_up_2 = True
                if event.key == pygame.K_k: 
                    moving_down_2 = True
                if event.key == pygame.K_RCTRL:
                    shoot2 = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_j:
                    moving_left_2 = False
                if event.key == pygame.K_l:
                    moving_right_2 = False
                if event.key == pygame.K_i:
                    moving_up_2 = False
                if event.key == pygame.K_k:
                    moving_down_2 = False
                if event.key == pygame.K_RCTRL:
                    shoot2 = False
    

    if player1.alive == False or player2.alive == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    pygame.display.update()

pygame.quit()