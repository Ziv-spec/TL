import pygame 
import sys

from pygame.locals import *
from scripts.camera import *


def main():

    screen = pygame.display.set_mode([800 , 600])
    camera = Camera([0,0],[400 , 300])
    
    while True:
        
        camera.erase_surf([255]*3)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)

        camera.display(screen , screen.get_rect())
        
        pygame.display.flip()


if __name__ == "__main__":
    main()
