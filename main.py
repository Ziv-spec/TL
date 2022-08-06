import pygame 
import sys
import time

from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import TileMap


def main():
    
    pygame.init()

    screen = pygame.display.set_mode([800 , 600] , vsync=True)
    camera = Camera([0,0],[400 , 300])
    
    tilemap = TileMap(chunk_size=[5,5])
    tilemap.load_map("./data/maps/level-test.tmx")
    timepoint = time.time()
    font = pygame.font.Font(None , 30)
    
    player = Player(Collider(FloatRect(pygame.Vector2(416 , 1280) , pygame.Vector2(16 , 16)) , "block"))
    chunk_pos = 0
    
    while True:
        
        chunk_pos = player.hitbox.rect.pos // (4*32)
        dt = time.time() - timepoint
        timepoint = time.time()
        
        camera.erase_surf([95, 138, 163])
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    player.km["left"] = True
                if event.key == K_d:
                    player.km["right"] = True
                if event.key == K_z:
                    player.km["up"] = True
                if event.key == K_s:
                    player.km["down"] = True
            elif event.type == KEYUP:
                if event.key == K_q:
                    player.km["left"] = False
                if event.key == K_d:
                    player.km["right"] = False
                if event.key == K_z:
                    player.km["up"] = False
                if event.key == K_s:
                    player.km["down"] = False  
        
        colliders = []
        
        for y in range(-1 , 2):
            for x in range(-1 , 2):
                try:
                    colliders.extend(tilemap.collider_chunks[f"{int(chunk_pos.x+x)},{int(chunk_pos.y+y)}"])
                except:
                        pass
        
        player.update(dt)
        player.move(colliders)
        
        camera.pos = player.hitbox.rect.pos + player.hitbox.rect.size / 2 - camera.size / 2
            
        if camera.pos.x < 0:
            camera.pos.x = 0
        if camera.pos.x > tilemap.size[0]*32-camera.size.x:
            camera.pos.x = tilemap.size[0]*32-camera.size.x
        if camera.pos.y < 0:
            camera.pos.y = 0
        if camera.pos.y > tilemap.size[1]*32-camera.size.y:
            camera.pos.y = tilemap.size[1]*32-camera.size.y

        
        tilemap.display(camera.render_surf , camera.pos)
        player.display(camera.render_surf , camera.pos)
        
        camera.display(screen , screen.get_rect())
        
        pygame.display.flip()


if __name__ == "__main__":
    main()
