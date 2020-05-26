import neat
import graphviz
# import matplotlib.pyplot as plt
# import numpy as np
import copy


class NeuronNetWork:

    def __init__(self, config_path):
        self.config_path = config_path

    def run(self, game):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation, self.config_path)
        game.bird_pop = neat.Population(config)
        game.bird_pop.add_reporter(neat.StatisticsReporter())
        game.bird_pop.add_reporter(neat.StdOutReporter(True))

        self.winner = game.bird_pop.run(game.eval_neat, 50)
