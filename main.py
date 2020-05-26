import pygame
from settings import *
from os import path
from sys import exit
import sprites
from random import randrange
import ann
from neat.nn import FeedForwardNetwork


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.load_data()
        self.playing = True
        self.clock = pygame.time.Clock()

    @staticmethod
    def load_img(dir, filename):
        return pygame.image.load(path.join(dir, filename)).convert_alpha()

    def load_data(self):
        img_dir = path.join(path.dirname(__file__), 'imgs')
        self.img_bird = [self.load_img(img_dir, 'bird1.png'),
                         self.load_img(img_dir, 'bird2.png'),
                         self.load_img(img_dir, 'bird3.png')]
        self.img_pipe = self.load_img(img_dir, 'pipe.png')
        self.img_base = self.load_img(img_dir, 'base.png')
        self.img_bg = self.load_img(img_dir, 'bg.png')
        self.neat = ann.NeuronNetWork(path.join(path.dirname(__file__), 'neat_config.txt'))

    def new(self, genomes, config):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        # self.all_sprites = pygame.sprite.Group()
        self.birds = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.bird_pool = {}
        self.nets = {}
        for genome_id, genome in genomes:
            genome.fitness = 0
            self.bird_pool[genome_id] = sprites.Player(self)
            self.nets[genome_id] = FeedForwardNetwork.create(genome, config)
        # self.player = sprites.Player(self)
        self.pipes_pool = [sprites.PipePair(self, WIDTH/2), sprites.PipePair(self, WIDTH+50)]
        self.pipe_gen_time = pygame.time.get_ticks()
        self.base_pool = [sprites.Base(self, 0), sprites.Base(self, 336)]

    def pipes_generator(self):
        now = pygame.time.get_ticks()
        if now - self.pipe_gen_time > randrange(2500, 4000):
            self.pipes_pool.append(sprites.PipePair(self, WIDTH+50))
            self.pipe_gen_time = now

    def run(self):
        self.neat.run(self)

    def eval_neat(self, genomes, config):
        self.new(genomes, config)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update(genomes)
            self.draw()
        self.nets = {}
        self.bird_pool = {}
        self.pipes_pool = []
        self.playing = True

    def pipe_death_check(self):
        if self.pipes_pool[0].pipe_up.rect.right < -10:
            self.pipes_pool[0].kill()
            self.pipes_pool.pop(0)

    def player_death_check(self):
        pass

    def get_dist(self):
        if self.pipes_pool[0].pipe_up.rect.left + 26< POSITION_X:
            pair = self.pipes_pool[1]
            return pair.pipe_up.rect.left + 26, pair.pipe_up.rect.bottom, pair.pipe_down.rect.top
        else:
            pair = self.pipes_pool[0]
            return pair.pipe_up.rect.left + 26, pair.pipe_up.rect.bottom, pair.pipe_down.rect.top

    def update(self, genomes):
        self.pipes_generator()
        self.pipe_death_check()
        if not len(self.bird_pool) > 0:
            self.playing = False
        dist, top, down = self.get_dist()
        for bird_id, genome in genomes:
            if not self.bird_pool.get(bird_id):
                continue
            indicator = False
            bird = self.bird_pool[bird_id]
            output = self.nets[bird_id].activate((bird.pos.y, dist, bird.vel.y,
                                                  bird.pos.y-top, bird.pos.y-down))
            if output[0] > .5:
                indicator = True
            res = bird.update(indicator)
            if res:
                genome.fitness -= 10
                self.bird_pool[bird_id].kill()
                self.bird_pool.pop(bird_id)
            else:
                genome.fitness += .1
        self.mobs.update()

    def draw(self):
        self.screen.blit(pygame.transform.scale(self.img_bg, (WIDTH, HEIGHT)), (0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def quit(self):
        self.playing = False
        pygame.quit()
        exit()


if __name__ == '__main__':
    g = Game()
    g.run()