import pygame 
import sys
import time

from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import TileMap
from scripts.text import *


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
    
    player = Player(Collider(FloatRect(pygame.Vector2(int(tilemap.object_datas["player_spawn"]["x"]) , int(tilemap.object_datas["player_spawn"]["y"])) , pygame.Vector2(16 , 16)) , "block"))
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
    
    control = True
    
    power = {"hide":{"cooldown":2 , "timer":0 , "time":5 , "active":False}}
    
    level_ended = False
    
    font = Font("./data/fonts/large_font.png")
    
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
                if control:
                    if event.key == K_q:
                        player.km["left"] = True
                    if event.key == K_d:
                        player.km["right"] = True
                    if event.key == K_z:
                        player.km["up"] = True
                    if event.key == K_s:
                        player.km["down"] = True
                if event.key == K_o:
                    for obj in objectlist.values():
                        pos = pygame.Vector2(float(value["x"])+float(value["width"])/2 , float(value["y"])+float(value["height"])/2)
                        if pos.distance_to(player.hitbox.rect.pos) <= 48:
                            obj["texture"] = tilemap.tileset[39]
                            if obj["tea recipe"]:
                                level_ended = True
                                control = False
                if event.key == K_p:
                    if power["hide"]["cooldown"] - power["hide"]["timer"] and not power["hide"]["active"]:
                        power["hide"]["timer"] = 0
                        power["hide"]["active"] = True
                        player.hidden = True
                        
            elif event.type == KEYUP:
                if control:
                    if event.key == K_q:
                        player.km["left"] = False
                    if event.key == K_d:
                        player.km["right"] = False
                    if event.key == K_z:
                        player.km["up"] = False
                    if event.key == K_s:
                        player.km["down"] = False
        
        if not level_ended:
            power["hide"]["timer"] += dt
            
            if power["hide"]["active"] and power["hide"]["time"] - power["hide"]["timer"] <= 0:
                player.hidden = False
                power["hide"]["active"] = False
            
            colliders = []
            
            for y in range(-1 , 2):
                for x in range(-1 , 2):
                    try:
                        colliders.extend(tilemap.collider_chunks[f"{int(chunk_pos.x+x)},{int(chunk_pos.y+y)}"])
                    except:
                        pass
            
            player.update(dt)
            player.move(colliders)
            
            if not power["hide"]["active"]:
                colliders.append(player.hitbox)
            
            enemy.update(dt , colliders)
            
            camera.pos = player.hitbox.rect.pos + player.hitbox.rect.size / 2 - camera.size / 2
                
            if camera.pos.x < 0:
                camera.pos.x = 0
            if camera.pos.x > tilemap.size[0]*32-camera.size.x:
                camera.pos.x = tilemap.size[0]*32-camera.size.x
            if camera.pos.y < 0:
                camera.pos.y = 0
            if camera.pos.y > tilemap.size[1]*32-camera.size.y:
                camera.pos.y = tilemap.size[1]*32-camera.size.y
        else:
            ...       
        
        tilemap.display(camera.render_surf , camera.pos)
        
        y = 0
        player_displayed = False
        for value in objectlist.values():
            y = float(value["y"])
            if not player_displayed and y > player.hitbox.rect.bottom:
                player.display(camera.render_surf , camera.pos)
                player_displayed = True
            camera.render_surf.blit(value["texture"] , pygame.Vector2(float(value["x"]) , float(value["y"])-float(value["height"])) - camera.pos)
        
        
        if not player_displayed:
            player.display(camera.render_surf , camera.pos)
            player_displayed = True
        
        enemy.display(camera.render_surf , camera.pos)
        
        enemy.display_light(black_filter , camera.pos)
        
        for collider in colliders:
            collider.rect.draw(camera.render_surf , camera.pos , True)
        
        camera.render_surf.blit(black_filter , [0,0])
        
        camera.display(screen , screen.get_rect())
        screen.blit(font.render(f"player position : {int(player.hitbox.rect.x)} , {int(player.hitbox.rect.y)}" , True , [255 , 0 , 0]) , [0,0])
        pygame.display.flip()


if __name__ == "__main__":
    main()
