from settings import *
import pygame
from os import path
import sprites
from sys import exit
from random import randint
import neat


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.load_data()
        self.neat_init()
        self.playing = True
        self.last_pipe_get = 0
        self.delta_time = 0
        self.pipes_pair = []
        self.birds_list = []

    def neat_init(self):
        neat_config_path = path.join(path.dirname(__file__), 'neat_config.txt')
        self.neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                              neat_config_path)
        self.bird_pop = neat.Population(self.neat_config)
        self.bird_pop.add_reporter(neat.StdOutReporter(True))
        self.bird_pop.add_reporter(neat.StatisticsReporter())

    def load_data(self):
        dir = path.join(path.dirname(__file__), 'imgs')
        self.bird_imgs = [pygame.image.load(path.join(dir, 'bird1.png')).convert_alpha(),
                          pygame.image.load(path.join(dir, 'bird2.png')).convert_alpha(),
                          pygame.image.load(path.join(dir, 'bird3.png')).convert_alpha()]
        self.bg_img = pygame.image.load(path.join(dir, 'bg.png')).convert_alpha()
        self.base_img = pygame.image.load(path.join(dir, 'base.png')).convert_alpha()
        self.base_img = pygame.transform.scale(self.base_img, (WIDTH, int(WIDTH/336*112//1)))
        self.pipe_img = pygame.image.load(path.join(dir, 'pipe.png')).convert_alpha()

    def game_reset(self):
        self.pipes_pair = []

    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.birds = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.game_reset()
        self.bird_pop.run(self.run, 50)
        # self.run()

    def pipes_generator(self):
        now = pygame.time.get_ticks()
        if now - self.last_pipe_get > randint(2000, 3500):
            top = HEIGHT / 2 + randint(-50, 50) - 100
            pt = sprites.Pipe(self, 'up', WIDTH + 100, top)
            pd = sprites.Pipe(self, 'down', WIDTH + 100, top + randint(PIPE_GAP_LOWBOUND, PIPE_GAP_UPBOUND))
            self.last_pipe_get = now
            self.pipes_pair.append([pt, pd])

    def update(self):
        self.pipes_generator()
        dist, up, down = self.pipes_pair[0][0].rect.left - WIDTH / 6, self.pipes_pair[0][0].rect.bottom,\
                         self.pipes_pair[0][1].rect.top
        if len(self.birds) > 0 and dist < 0:
            dist, up, down = self.pipes_pair[1][0].rect.left - WIDTH / 6, self.pipes_pair[1][0].rect.bottom, \
                             self.pipes_pair[1][1].rect.top
        for num, sprite in enumerate(self.birds_list):
            sprite.update(num, dist, up, down)
        for g in self.ge:
            g.fitness += .1
        self.mobs.update()

    def draw(self):
        self.screen.blit(pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT)), self.bg_img.get_rect())
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def neat_info(self):
        self.ge = []
        self.nets = []
        for _, g in self.genomes:
            net = neat.nn.FeedForwardNetwork.create(g, self.neat_config)
            self.nets.append(net)
            bird = sprites.Bird(self, WIDTH / 6, HEIGHT / 2)
            self.birds_list.append(bird)
            g.fitness = 0
            self.ge.append(g)
        sprites.Base(self, 0)
        pt = sprites.Pipe(self, 'up', WIDTH - 50, HEIGHT / 2 - randint(100, 200))
        pd = sprites.Pipe(self, 'down', WIDTH - 50, HEIGHT / 2 + randint(10, 50))
        self.pipes_pair.append([pt, pd])
        self.last_pipe_get = pygame.time.get_ticks()

    def run(self, ge, config):
        self.game_reset()
        self.genomes = ge
        self.neat_config = config
        self.neat_info()
        while self.playing and len(self.birds_list) > 0:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def quit(self):
        pygame.quit()
        exit()


if __name__ == '__main__':
    g = Game()
    g.new()