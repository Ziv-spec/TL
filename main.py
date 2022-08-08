from ast import excepthandler
from asyncore import loop
import pygame 
import sys
import time

from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import TileMap
from scripts.text import *
from scripts.button import *


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


    # load 
    enemies_path = []
    for e in enemies_datas: 

        enemy_path = []
        before = []
        after = []
        start_point_found = False
        for p in enemies_datas[e]:
            if p['type'] == 'enemy_path':
                x, y, width, height = p['x'], p['y'], p['width'], p['height']
                start_point = p['startpoint']

                if not start_point_found and start_point['value'] == 'false':  
                    before.append((int(x), int(y), int(width), int(height)))
                elif start_point['value'] == 'false': 
                    after.append((int(x), int(y), int(width), int(height)))

                if start_point['value'] == 'true':
                    enemy_path.append((int(x), int(y), int(width), int(height)))
                    start_point_found = True
        print(before, after, enemy_path)
        enemy_path.extend(reversed(before))
        enemy_path.extend(reversed(after)) # TODO: check whether I need to reverse after or not 
        enemies_path.append(enemy_path)
        
    objectlist = {k : v for k , v in sorted(objectlist.items() , key=sort_object) if "chest" in k}

    enemy = Enemy(Collider(FloatRect(pygame.Vector2(752.0, 784.0) , pygame.Vector2(16 , 16)) , "block"))
    
    enemy.set_direction(pygame.Vector2(0 , -1))
    enemy.set_path(enemies_path[0])
    
    control = True
    
    power = {"hide":{"cooldown":2 , "timer":0 , "time":5 , "active":False}}
    
    level_ended = False
    
    lfont = Font("./data/fonts/large_font.png" , [255]*3)
    sfont = Font("./data/fonts/small_font.png" , [255]*3)
    
    finished_text = Text(lfont , "Congrulations ! You found the tea recipe !")
    finished_text.origin = finished_text.size/2
    finished_text.pos = pygame.Vector2(200 , 75)
    
    click_text = Text(sfont , "click for next level ... (or maybe ?)")
    click_text.origin = pygame.Vector2(click_text.size.x / 2 , 0)
    click_text.pos = pygame.Vector2(200 , 290 - click_text.size.y )
    
    gameover_text = Text(sfont , "Game over !!!")
    gameover_text.origin = gameover_text.size / 2
    gameover_text.pos = pygame.Vector2(200 , 150)
    
    panel_datas = {
        "surface":pygame.Surface([400 , 300] , SRCALPHA),
        "alpha":0,
        "panel_list":{
            "end_level":pygame.Surface([400 , 300] , SRCALPHA),
            "game_over":pygame.Surface([400 , 300] , SRCALPHA)
        }
    }
    
    panel_datas["panel_list"]["end_level"].fill([0,0,0])
    panel_datas["panel_list"]["game_over"].fill([0,0,0])
    finished_text.display(panel_datas["panel_list"]["end_level"])
    click_text.display(panel_datas["panel_list"]["end_level"])
    gameover_text.display(panel_datas["panel_list"]["game_over"])
    
    tea_cup = pygame.image.load("./data/tea.png").convert_alpha()
    panel_datas["panel_list"]["end_level"].blit(pygame.transform.scale(tea_cup , [128 , 128]) , [200-64 , 150])
    
    state = "menu"
    
    def start_game():
        nonlocal state
        state = "game"
    
    button_image = pygame.image.load("./data/start-button.png").convert_alpha()
    button_image = pygame.transform.scale(button_image , [button_image.get_width()*4 , button_image.get_height()*4])
    
    start_button_data = {
        "target":start_game,
        "text-data":{
            "content":"",
            "font":pygame.font.Font(None , 30),
            "centered":True
        },"textures":{
            "nothing":button_image,
            "hover":button_image,
            "clicked":button_image,
        }
    }
    
    button = Button([350 , 400] , [128 , 128] , start_button_data)
    
    menu_image = pygame.image.load("./data/menu.PNG").convert_alpha()
    
    while True:
        
        if state == "game":
            chunk_pos = player.hitbox.rect.pos // (4*32)
            dt = time.time() - timepoint
            timepoint = time.time()
        
        
            all_colliders = []
            for chunck in tilemap.collider_chunks.values():
                all_colliders.extend(chunck)


            all_colliders.append(player.hitbox)

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
                                    panel_datas["surface"] = panel_datas["panel_list"]["end_level"]
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
                
                
                enemy.update(dt, all_colliders, camera.pos)
                enemy.move(colliders)
                
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
                
                if panel_datas["alpha"] < 220:
                    panel_datas["alpha"] += 70 * dt

            
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
                
            if level_ended:
                surf = panel_datas['surface'].copy()
                surf.set_alpha(0+panel_datas["alpha"])
                camera.render_surf.blit(surf , [0,0])
            else:
                camera.render_surf.blit(black_filter , [0,0])
            
            camera.display(screen , screen.get_rect())
        
        else:
            
            screen.fill([0,0,0])
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                
                button.update(event)
            
            screen.blit(menu_image , [400-583/2 , 10])
            
            button.display(screen)
            
        
        pygame.display.flip()


if __name__ == "__main__":
    main()
