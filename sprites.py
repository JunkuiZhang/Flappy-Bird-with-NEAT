import pygame
from settings import *
from random import randrange
from pygame.math import Vector2
vec = Vector2


class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        self._layer = 3
        self.groups = game.all_sprites, game.birds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_count = 0
        self.last_img_update = 0
        self.last_jump = -100
        self.rot = 0
        self.pos = vec(POSITION_X, (HEIGHT - 100) / 2)
        self.get_image()
        self.vel = vec(BIRD_SPEED/20, 0)
        self.acc = vec(0, GRAVITY)

    def get_image(self):
        self.image = pygame.transform.rotate(self.game.img_bird[self.image_count], self.rot)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = self.pos.y
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self, now):
        self.vel.y = -BIRD_SPEEDY_CHANGE
        self.last_jump = now
        # if self.vel.y < -200:
        #     self.vel.y = -200
        # if self.vel.y > 200:
        #     self.vel.y = 200

    def check_bound(self):
        if self.pos.y < 0:
            return True
        return False

    def image_update(self, now):
        if now - self.last_img_update > 200:
            self.image_count += 1
            if self.image_count > 2:
                self.image_count = 0
            self.last_img_update = now
            _y = self.rect.centery
            self.rect.centery = _y
        self.get_image()

    def jump_duration_check(self, now):
        if now - self.last_jump > JUMP_DURATION:
            return True
        else:
            return False

    def update(self, indicator):
        # self.vel.y += BIRD_SPEEDY_DOWN_SPEED
        # now = pygame.time.get_ticks()
        # if self.jump_duration_check(now):
        #     self.jump()
        # elif indicator:
        #     self.jump()
        #     self.last_jump = now
        now = pygame.time.get_ticks()
        if indicator and self.jump_duration_check(now):
            self.jump(now)
        self.vel.y += self.acc.y
        self.rot = self.vel.angle_to(vec(1, 0))
        self.pos.y += self.vel.y + .5 * self.acc.y
        self.image_update(now)
        if pygame.sprite.spritecollideany(self, self.game.mobs, pygame.sprite.collide_mask) or self.check_bound():
            self.kill()
            return True
        return False


class Pipe(pygame.sprite.Sprite):

    def __init__(self, game, direction, x, y):
        self._layer = 1
        self.groups = game.all_sprites, game.mobs, game.pipes
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if direction == 'up':
            self.image = pygame.transform.flip(game.img_pipe, False, True)
            self.rect = self.image.get_rect()
            self.rect.bottom = y
        else:
            self.image = game.img_pipe
            self.rect = self.image.get_rect()
            self.rect.top = y
        self.rect.left = x
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.left -= BIRD_SPEED * self.game.dt


class PipePair:

    def __init__(self, game, x):
        mid = int(round((HEIGHT - 100) / 2, 0))
        gap = randrange(mid - 70, mid + 70)
        rand1 = randrange(50, 100)
        rand2 = -randrange(50, 100)
        if rand1 - rand2 < 120:
            rand1 = 60
            rand2 = -60
        self.pipe_up = Pipe(game, 'up', x, gap + rand2)
        self.pipe_down = Pipe(game, 'down', x, gap + rand1)

    def kill(self):
        self.pipe_up.kill()
        self.pipe_down.kill()


class Base(pygame.sprite.Sprite):

    def __init__(self, game, x):
        self._layer = 2
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.img_base
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = HEIGHT - 100
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass
