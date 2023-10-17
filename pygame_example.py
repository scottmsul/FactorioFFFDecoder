import os
import pygame
import sys
from pygame.locals import *

white = (255,255,255)
black = (0,0,0)
FACTORIO_BACKGROUND = (36, 35, 36)

class Pane(object):
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(os.path.join("fonts", "TitilliumTTF", 'TitilliumWeb-Regular.ttf'), 14)
        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((600,400), 0, 32)
        self.screen.fill((white))
        pygame.display.update()


    def addRect(self):
        pygame.draw.rect
        self.rect = pygame.draw.rect(self.screen, FACTORIO_BACKGROUND, (175, 75, 200, 100))
        pygame.display.update()

    def addText(self):
        self.screen.blit(self.font.render('Overview', True, (255,255,255)), (200, 100))
        pygame.display.update()

if __name__ == '__main__':
    Pan3 = Pane()
    Pan3.addRect()
    Pan3.addText()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
