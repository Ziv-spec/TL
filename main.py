import pygame 
import sys
import time

from pygame.locals import *
from scripts.camera import *
from scripts.map import TileMap


def main():
    
    pygame.init()

    screen = pygame.display.set_mode([800 , 600] , vsync=True)
    camera = Camera([0,0],[400 , 300])
    
    tilemap = TileMap(chunk_size=[5,5])
    tilemap.load_map("./data/maps/level-test.tmx")
    timepoint = time.time()
    
    keys = {"right":False , "left":False , "up":False , "down":False}
    font = pygame.font.Font(None , 30)
    
    while True:
        
        dt = time.time() - timepoint
        timepoint = time.time()
        
        camera.erase_surf([255]*3)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    keys["left"] = True
                if event.key == K_d:
                    keys["right"] = True
                if event.key == K_z:
                    keys["up"] = True
                if event.key == K_s:
                    keys["down"] = True
            elif event.type == KEYUP:
                if event.key == K_q:
                    keys["left"] = False
                if event.key == K_d:
                    keys["right"] = False
                if event.key == K_z:
                    keys["up"] = False
                if event.key == K_s:
                    keys["down"] = False   
                    
        if keys["down"]:
            camera.pos.y += 100*dt
        elif keys["up"]:
            camera.pos.y -= 100*dt
        elif keys["right"]:
            camera.pos.x += 100*dt
        elif keys["left"]:
            camera.pos.x -= 100*dt 
            
        if camera.pos.x < 0:
            camera.pos.x = 0
        if camera.pos.x > tilemap.size[0]*32-camera.size.x:
            camera.pos.x = tilemap.size[0]*32-camera.size.x
        if camera.pos.y < 0:
            camera.pos.y = 0
        if camera.pos.y > tilemap.size[1]*32-camera.size.y:
            camera.pos.y = tilemap.size[1]*32-camera.size.y

        tilemap.display(camera.render_surf , camera.pos)
        camera.display(screen , screen.get_rect())
        
        pygame.display.flip()


if __name__ == "__main__":
    main()
