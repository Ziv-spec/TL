from ast import excepthandler
from asyncore import loop
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
    
    black_filter = pygame.Surface([400 , 300] , SRCALPHA)
    black_filter.fill([0,0,0,120])
    
    tilemap = TileMap(chunk_size=[5,5])
    tilemap.load_map("./data/maps/level-test.tmx")
    timepoint = time.time()
    font = pygame.font.Font(None , 30)
    
    player = Player(Collider(FloatRect(pygame.Vector2(416 , 1280) , pygame.Vector2(16 , 16)) , "block"))
    player.hitbox_offset = pygame.Vector2(
        16 - player.hitbox.rect.size.x / 2,
        48 - player.hitbox.rect.size.y 
    )
    
    chunk_pos = 0
    
    def sort_object(item):
        if "chest" in item[0]:
            return float(item[1]["y"])+32
        else:
            return 0
    
    objectlist = {k : v for k , v in tilemap.object_datas.items()}
    
    enemies_datas = {k : v for k , v in objectlist.items() if "enemy" in k}
    
    objectlist = {k : v for k , v in sorted(objectlist.items() , key=sort_object) if "chest" in k}

    enemy = Enemy(Collider(FloatRect(pygame.Vector2(416+128 , 1280-128) , pygame.Vector2(16 , 16)) , "block"))
    enemy.set_direction(pygame.Vector2(0 , -1))
    
    while True:
        
        chunk_pos = player.hitbox.rect.pos // (4*32)
        dt = time.time() - timepoint
        timepoint = time.time()
        
        camera.erase_surf([38, 27, 74])
        black_filter.fill([0,0,0,120])
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_a:
                    player.km["left"] = True
                if event.key == K_d:
                    player.km["right"] = True
                if event.key == K_w:
                    player.km["up"] = True
                if event.key == K_s:
                    player.km["down"] = True
            elif event.type == KEYUP:
                if event.key == K_a:
                    player.km["left"] = False
                if event.key == K_d:
                    player.km["right"] = False
                if event.key == K_w:
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
        
        all_colliders = []
        for chunck in tilemap.collider_chunks.values():
            all_colliders.extend(chunck)

        player.update(dt)
        player.move(colliders)

        all_colliders.append(player.hitbox)
        enemy.update(dt, all_colliders)
        enemy.move(colliders)

        
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
        
        y = 0
        player_displayed = False
        for value in objectlist.values():
            y = float(value["y"])+float(value["height"])
            if not player_displayed and y > player.hitbox.rect.bottom:
                player.display(camera.render_surf , camera.pos)
                player_displayed = True
            camera.render_surf.blit(value["texture"] , pygame.Vector2(float(value["x"]) , float(value["y"])) - camera.pos)
        
        if not player_displayed:
            player.display(camera.render_surf , camera.pos)
            player_displayed = True
        
        enemy.display(camera.render_surf , camera.pos)
        
        enemy.display_light(black_filter , camera.pos)
        
        camera.render_surf.blit(black_filter , [0,0])
        
        camera.display(screen , screen.get_rect())
        screen.blit(font.render(f"player position : {int(player.hitbox.rect.x)} , {int(player.hitbox.rect.y)}" , True , [255 , 0 , 0]) , [0,0])
        pygame.display.flip()


if __name__ == "__main__":
    main()
