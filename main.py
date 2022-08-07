from ast import excepthandler
from asyncore import loop
import pygame 
import sys
import time

from pygame.locals import *
from scripts.camera import *
from scripts.entity import *
from scripts.map import TileMap

from pygame import Vector2
from math import atan, asin, pi 

class Enemy():
    def __init__(self, hitbox: Collider):
        self.hitbox = hitbox
        self.hitbox_offset = pygame.Vector2(0,0)
        self.v = Vector2()

        self.texture = pygame.Surface((32, 32))
        self.texture.fill((255, 0, 0)) # red
        self.velocity = Vector2()
        self.view_angle = 60# in degrees

        self.direction = Vector2(1,19)

    def update(self, dt, colliders):
        
        # construct enemy view 
        ewidth, eheight = self.hitbox.rect.size
        self.ecenter = Vector2(self.hitbox.rect.x+ewidth//2, self.hitbox.rect.y+eheight//2)

        view_angle_radians = self.view_angle*pi/180
        direction_in_radians = 0
        if self.direction.x != 0:
            direction_in_radians = atan(self.direction.y / self.direction.x)

        right = direction_in_radians - view_angle_radians/2
        left  = direction_in_radians + view_angle_radians/2
        right_direction, left_direction = Vector2(1, (-right)).normalize(), Vector2(1, (-left)).normalize()
        self.right = right_direction
        self.left = left_direction

        def learp(a, b, t):
            return a + t * (b - a)

        def collide_line_with_line(line1, line2):
            x1, y1, x2, y2 = line1
            x3, y3, x4, y4 = line2
            
            uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
            uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
            if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1): 
                intersectionX = x1 + (uA * (x2-x1))
                intersectionY = y1 + (uA * (y2-y1))
                return Vector2(intersectionX, intersectionY)
            return Vector2()

        def collide_ray_with_rect(ray, _colliders):
            # TODO: return the closest point to the ray
            for c in colliders:
                x, y, w, h = c.rect.pos.x, c.rect.pos.y, c.rect.size[0], c.rect.size[1] 
                lines = [
                    [x, y, x, y+h], 
                    [x, y, x+w, y],
                    [x+w, y, x+w, y+h],
                    [x, y+h, x+w, y+h],
                ]
                min_len = 100000000000
                for line in lines:
                    point = collide_line_with_line(ray, line)
                    if point == Vector2():
                        continue
                    new_len = (point - Vector2(ray[0], ray[1])).length() 
                    if new_len < min_len:
                        min_len = new_len 
                        min_len_point = point
                if point != Vector2(): return min_len_point
            return Vector2()

        radius = 150
        loop_amount = 100
        points = []
        empty_vector = Vector2()

        for i in range(0, loop_amount):
            t = i/loop_amount
            ray_direction = learp(right_direction, left_direction, t)
            x1, y1 = self.ecenter
            x2, y2 = self.ecenter + ray_direction * radius
            r=  (x1, y1, x2, y2)

            point = collide_ray_with_rect(r, colliders)
            if point != empty_vector:
                points.append(point)
        self.points = points


        # direction = Vector2(player.hitbox.rect.x, player.hitbox.rect.y) - Vector2(self.hitbox.rect.x, self.hitbox.rect.y)
        # if direction.x**2 + direction.y**2 > 0:
        #     direction = direction.normalize()
        # self.a = direction*100*dt
        # self.velocity += self.a * dt



    def get_colliders(self , colliders):
        collided = []
        for collider in colliders:
            if self.hitbox.collide(collider):
                collided.append(collider)
        
        return collided

    def move(self , colliders):
        
        self.hitbox.rect.x += self.velocity.x
        collided = self.get_colliders(colliders)
        for collider in collided:
            if self.velocity.x < 0:
                self.hitbox.rect.x = collider.rect.right
            elif self.velocity.x > 0:
                self.hitbox.rect.right = collider.rect.x
        
        self.hitbox.rect.y += self.velocity.y
        collided = self.get_colliders(colliders)
        for collider in collided:
            if self.velocity.y < 0:
                self.hitbox.rect.y = collider.rect.bottom
            elif self.velocity.y > 0:
                self.hitbox.rect.bottom = collider.rect.y
    
    def display(self , surface : pygame.Surface , offset : pygame.Vector2):
        text_pos = self.hitbox.rect.pos - self.hitbox_offset - offset
        surface.blit(self.texture , text_pos)

        self.ecenter -= offset
        pygame.draw.line(surface, (0, 0, 255),self.ecenter, self.ecenter+ self.right*100)
        pygame.draw.line(surface, (0, 0, 255),self.ecenter, self.ecenter+ self.left*100)
        for point in self.points:
            # print(point)
            pygame.draw.circle(surface, (0, 0, 255), point-offset, 3, 3)


def main():
    
    pygame.init()

    screen = pygame.display.set_mode([800 , 600] , vsync=True)
    camera = Camera([0,0],[400 , 300])
    
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
        if not "enemy" in item[0]:
            return float(item[1]["y"])+32
        else:
            return 0
    
    objectlist = {k : v for k , v in tilemap.object_datas.items()}
    
    enemies_datas = {k : v for k , v in objectlist.items() if "enemy" in k}
    
    objectlist = {k : v for k , v in sorted(objectlist.items() , key=sort_object) if not "enemy" in k}

    enemy = Enemy(Collider(FloatRect(pygame.Vector2(416 , 1280) , pygame.Vector2(16 , 16)) , "block"))
    
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
        
        enemy.update(dt, colliders)

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
        
        camera.display(screen , screen.get_rect())
        screen.blit(font.render(f"player position : {int(player.hitbox.rect.x)} , {int(player.hitbox.rect.y)}" , True , [255 , 0 , 0]) , [0,0])
        pygame.display.flip()


if __name__ == "__main__":
    main()
