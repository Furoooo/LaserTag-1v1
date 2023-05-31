import pygame
import sys
import time
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
WHITE = (255, 255, 255)

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
                self.rect.right = tile.left
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
                bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction_x), 
                                self.rect.centery, self.direction_x, self.direction_y, display, piattaforma)
                sparo.play()
            else:
                bullet = Bullet(self.rect.centerx, self.rect.centery - (0.6 * self.rect.size[0] * self.direction_y), 
                                self.direction_x, self.direction_y, display, piattaforma)
                sparo.play()
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
            game_over()

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
                hurt.play()
        
        if pygame.sprite.spritecollide(player1, bullet_group, False):
            if player1.alive:
                player1.health -= 10
                self.kill()
                hurt.play()


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

player1 = giocatore(display, piattaforma, 'player1', 50, 50, 2.3, 2)
player2 = giocatore(display, piattaforma, 'player2', 1150, 630, 2.3, 2)
health_bar1 = HealthBar1(10, 10, player1.health, player1.health)
health_bar2 = HealthBar2(1040, 10, player2.health, player2.health)

font = pygame.font.SysFont('reemkufi', 50)
game_over_font = pygame.font.SysFont('reemkufi', 80)

def draw_text(text):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_LARG/2, SCREEN_ALTE/1.3))
    image1 = pygame.image.load('imgs/controls/wasd.png')
    image2 = scale_image(pygame.image.load('imgs/controls/spacebar.png'), 0.9)
    image3 = pygame.image.load('imgs/controls/ijkl.png')
    image4 = pygame.image.load('imgs/controls/lshift.png')

    image5 = pygame.image.load('imgs/controls/player1.png')
    image6 = pygame.image.load('imgs/controls/player2.png')

    image7 = scale_image(pygame.image.load('imgs/player1/side/0.png'), 5)
    image8 = scale_image(pygame.transform.flip(pygame.image.load('imgs/player2/side/0.png'), True, False), 5)

    rect1 = image1.get_rect()
    rect1.topleft = (10, 150)
    rect2 = image2.get_rect()
    rect2.topleft = (40, 325)
    rect3 = image3.get_rect()
    rect3.topright = (1190, 150)
    rect4 = image4.get_rect()
    rect4.topright = (1154, 325)

    rect5 = image5.get_rect()
    rect5.topleft = (10, 70)
    rect6 = image6.get_rect()
    rect6.topright = (1190, 70)

    rect7 = image7.get_rect()
    rect7.topleft = (200, 10)
    rect8 = image8.get_rect()
    rect8.topright = (1000, 10)

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, GREEN, (10, 10, 150, 20))
    pygame.draw.rect(screen, GREEN, (1040, 10, 150, 20))
    screen.blit(image1, rect1)
    screen.blit(image2, rect2)
    screen.blit(image3, rect3)
    screen.blit(image4, rect4)
    screen.blit(image5, rect5)
    screen.blit(image6, rect6)
    screen.blit(image7, rect7)
    screen.blit(image8, rect8)
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def wait_for_input():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    waiting = False

pygame.mixer.music.load("musica.wav")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

draw_text("Press BACKSPACE to start!")
wait_for_input()

sparo = pygame.mixer.Sound('sparo.wav')
sparo.set_volume(0.5)
hurt = pygame.mixer.Sound('hurt.wav')
hurt.set_volume(0.6)

gameover = False

def game_over():
    global gameover
    
    if player1.alive == False and player2.alive == True:
        image1 = scale_image(pygame.image.load('imgs/player1/Dead/0.png'), 5)
        rect1 = image1.get_rect()
        rect1.topleft = (200, 10)
        screen.blit(image1, rect1)
        pygame.draw.rect(screen, RED, (10, 10, 150, 20))
        image2 = scale_image(pygame.transform.flip(pygame.image.load('imgs/player2/Side/0.png'), True, False), 5)
        rect2 = image2.get_rect()
        rect2.topright = (1000, 10)
        screen.blit(image2, rect2)
        ratio = player2.health / 50
        diff = 150 - (150 * ratio)
        pygame.draw.rect(screen, RED, (1040, 10, 150, 20))
        pygame.draw.rect(screen, GREEN, (1040 + diff, 10, 150 * ratio, 20)) 
        display_game_over = game_over_font.render("Player 2 won!", True, WHITE, BLACK)

    if player2.alive == False and player1.alive == True:
        image1 = scale_image(pygame.image.load('imgs/player1/Side/0.png'), 5)
        rect1 = image1.get_rect()
        rect1.topleft = (200, 10)
        screen.blit(image1, rect1)
        ratio = player1.health / 50
        pygame.draw.rect(screen, RED, (10, 10, 150, 20))
        pygame.draw.rect(screen, GREEN, (10, 10, 150 * ratio, 20))

        image2 = scale_image(pygame.transform.flip(pygame.image.load('imgs/player2/Dead/0.png'), True, False), 5)
        rect2 = image2.get_rect()
        rect2.topright = (1000, 10)
        screen.blit(image2, rect2)
        pygame.draw.rect(screen, RED, (1040, 10, 150, 20)) 
        display_game_over = game_over_font.render("Player 1 won!", True, WHITE, BLACK)

    if player1.alive == False and player2.alive == False:
        image1 = scale_image(pygame.image.load('imgs/player1/Dead/0.png'), 5)
        rect1 = image1.get_rect()
        rect1.topleft = (200, 10)
        screen.blit(image1, rect1)
        pygame.draw.rect(screen, RED, (10, 10, 150, 20))

        image2 = scale_image(pygame.transform.flip(pygame.image.load('imgs/player2/Dead/0.png'), True, False), 5)
        rect2 = image2.get_rect()
        rect2.topright = (1000, 10)
        screen.blit(image2, rect2)
        
        pygame.draw.rect(screen, RED, (1040, 10, 150, 20)) 
        display_game_over = game_over_font.render("It's a draw!", True, WHITE, BLACK)

    image5 = pygame.image.load('imgs/controls/player1.png')
    image6 = pygame.image.load('imgs/controls/player2.png')
    rect5 = image5.get_rect()
    rect5.topleft = (10, 70)
    rect6 = image6.get_rect()
    rect6.topright = (1190, 70)
    screen.blit(image5, rect5)
    screen.blit(image6, rect6)

   
    display_restart = font.render("Press BACKSPACE to restart", True, WHITE, BLACK)
    display_quit = font.render("Press ESC to close the game", True, WHITE, BLACK)
    rect_restart = display_restart.get_rect()
    rect_game_over = display_game_over.get_rect()
    rect_quit = display_quit.get_rect()
    rect_quit.center = (SCREEN_LARG/2, 600)
    rect_restart.center = (SCREEN_LARG/2, 525)
    rect_game_over.center = (SCREEN_LARG/2, 300)
    screen.blit(display_game_over, rect_game_over)
    screen.blit(display_restart, rect_restart)
    screen.blit(display_quit, rect_quit)
    gameover = True

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
                    moving_left_1 = True
                if event.key == pygame.K_d:
                    moving_right_1 = True
                if event.key == pygame.K_w:
                    moving_up_1 = True
                if event.key == pygame.K_s:
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
                if event.key == pygame.K_RSHIFT:
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
                if event.key == pygame.K_RSHIFT:
                    shoot2 = False

    if player1.alive == False or player2.alive == False:
        screen.fill((0,0,0))

        player1.check_alive()
        player2.check_alive()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE and gameover:
                    shoot1 = False
                    shoot2 = False

                    moving_left_1 = False
                    moving_right_1 = False
                    moving_up_1 = False
                    moving_down_1 = False

                    moving_left_2 = False
                    moving_right_2 = False
                    moving_up_2 = False
                    moving_down_2 = False

                    bullet_group.empty()
                    player1 = giocatore(display, piattaforma, 'player1', 50, 50, 2.3, 2)
                    player2 = giocatore(display, piattaforma, 'player2', 1150, 630, 2.3, 2)

                    gameover = False
                if event.key == pygame.K_ESCAPE:
                    run = False

    pygame.display.update()

pygame.quit()