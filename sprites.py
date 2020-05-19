import pygame
from settings import *
from pygame.math import Vector2
vec = Vector2


class Bird(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = 3
        self.groups = game.all_sprites, game.birds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vec(x, y)
        self.image = self.game.bird_imgs[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)
        self.vel_y = vec(0, 0)
        self.rot = 0

    def jump(self, indicator):
        if indicator:
            self.vel_y -= vec(0, BIRD_SPEEDY_CHANGE)
        self.vel_y += vec(0, BIRD_SPEEDY_DOWN_SPEED)
        if self.vel_y.y < -200:
            self.vel_y.y = -200

    def img_update(self):
        v_x = vec(BIRD_SPEED, 0)
        v_y = vec(0, self.vel_y.y)
        vel = v_x + v_y
        self.rot = vel.angle_to(v_x)
        self.image = pygame.transform.rotate(self.game.bird_imgs[0], self.rot)
        self.mask = pygame.mask.from_surface(self.image)

    def check_bound(self):
        if self.pos.y <= 0:
            return True
        else:
            return False

    def update(self, index, dist, up, down):
        output = self.game.nets[index].activate((self.pos.y, dist, abs(up-self.pos.y), abs(down-self.pos.y)))
        self.jump(output[0] > .5)
        self.pos += self.vel_y * self.game.dt
        self.img_update()
        self.rect = self.image.get_rect()
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y
        if pygame.sprite.spritecollideany(self, self.game.mobs, pygame.sprite.collide_mask) or self.check_bound():
            self.game.ge[index].fitness -= 1
            self.game.ge.pop(index)
            self.game.nets.pop(index)
            self.game.birds_list.pop(index)
            self.kill()


class Pipe(pygame.sprite.Sprite):

    def __init__(self, game, indicator, x, y):
        self.groups = game.all_sprites, game.mobs
        self.game = game
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.indicator = indicator
        if indicator == 'up':
            self.image = pygame.transform.flip(self.game.pipe_img, False, True)
        else:
            self.image = self.game.pipe_img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        if indicator == 'up':
            self.rect.bottom = y
        else:
            self.rect.top = y

    def update(self, *args):
        self.rect.centerx -= (BIRD_SPEED + self.game.delta_time) * self.game.dt
        if self.rect.right < 0:
            if self.indicator == 'up':
                self.game.pipes_pair.pop(0)
            self.kill()


class Base(pygame.sprite.Sprite):

    def __init__(self, game, x):
        self.groups = game.all_sprites, game.mobs
        self.game = game
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = self.game.base_img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = HEIGHT - 100

    def update(self, *args):
        pass
