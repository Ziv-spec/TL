import pygame

from scripts.animation import *
from scripts.form import *
from pygame.locals import *
from scripts.unclassed_functions import mult_image
from pygame import Vector2
from math import cos, sin


class Player:
    
    def __init__(self , hitbox : Collider):
        
        self.hitbox = hitbox
        self.hitbox_offset = pygame.Vector2(0,0)
        
        self.velocity = pygame.Vector2(0,0)
        self.km = {"right":False , "left":False , "up":False , "down":False}
        self.directions = {"right":1 , "left":-1 , "up":-1 , "down":1}
        self.angle = 0
        
        self.anim_manager = AnimationManager("./data/player")
        self.animation = self.anim_manager.get("idle")
        self.base_texture = pygame.image.load("./data/player.png").convert_alpha()
        self.texture = self.base_texture
    
    def set_animation(self , id : str):
        
        if self.animation.data.id != id:
            self.animation = self.anim_manager.get(id)
    
    def update(self , dt):
        
        result = pygame.Vector2(0,0)
        
        if self.km["down"]:
            result.y += self.directions["down"]
        if self.km["up"]:
            result.y += self.directions["up"]
        if self.km["right"]:
            result.x += self.directions["right"]
        if self.km["left"]:
            result.x += self.directions["left"]
        
        try:
            result.normalize_ip()
        except:
            pass
        self.velocity = result * 130 * dt
        
        if (abs(self.velocity.x)+abs(self.velocity.y) > 0):
            self.set_animation("running")
        else:
            self.set_animation("idle")
        
        self.flip = (self.velocity.x < 0)
        
        self.animation.play(dt)
        self.texture = self.animation.get_current_img(self.flip)
        
        self.flip = False
        
    
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
        
class Enemy():
    def __init__(self, hitbox: Collider):
        self.hitbox = hitbox
        self.hitbox_offset = pygame.Vector2(0,0)
        self.v = Vector2()

        self.texture = pygame.Surface((32, 32))
        self.texture.fill((255, 0, 0)) # red
        self.velocity = Vector2()
        self.view_angle = 60# in degrees

        self.direction = 0
        self.colliders = None

        self.current_index = 0 # for enemy path

        self.view_distance = 150
        self.original_texture = pygame.image.load("./data/enemy_view.png").convert_alpha()
        self.light = self.original_texture.copy()
        self.light = pygame.transform.scale(self.light , [self.view_distance*2]*2)
        self.light = mult_image(self.light , [100 , 100 , 100])


    def set_direction(self , direction : pygame.Vector2):
        self.direction = direction
        
        # angle = 0
        # try:
        #     angle = 90-degrees()
        # except:
        #     angle = 90
        if direction.y == -1:
            self.light = pygame.transform.flip(self.original_texture , False , True)
        elif direction.x == -1:
            self.light = pygame.transform.rotate(self.original_texture , 90)
        elif direction.x == 1:
            self.light = pygame.transform.flip(pygame.transform.rotate(self.original_texture , 90) , True , False)
        
        self.light = pygame.transform.scale(self.light , [self.view_distance*2]*2)
        
        self.light = mult_image(self.light , [100 , 100 , 100])
        
    @property
    def rect(self):
        return self.hitbox.rect

    def update(self, dt, colliders, offset):
        self.colliders = colliders
        
        # construct enemy view 
        ewidth, eheight = self.hitbox.rect.size
        self.ecenter = pygame.Vector2(self.hitbox.rect.x+ewidth//2, self.hitbox.rect.y+eheight//2)

       #direction angle
        da = pygame.Vector2(self.direction.x , -self.direction.y).angle_to(pygame.Vector2(0))
        self.right , self.left = pygame.Vector2(cos(radians(da+self.view_angle/2)),-sin(radians(da+self.view_angle/2))),pygame.Vector2(cos(radians(da-self.view_angle/2)),-sin(radians(da-self.view_angle/2)))

        def learp(a, b, t):
            return a + t * (b - a)

        def collide_line_with_line(line1, line2):
            # print(line1, line2)
            x1, y1, x2, y2 = line1
            x3, y3, x4, y4 = line2
            
            uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / (((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))+.001)
            uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / (((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))+.001)
            if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1): 
                intersectionX = x1 + (uA * (x2-x1))
                intersectionY = y1 + (uA * (y2-y1))
                return Vector2(intersectionX, intersectionY)
            return Vector2()

        def collide_ray_with_rect(ray, _colliders):
            min_len = 100000000000
            min_len_point = Vector2()
            for c in _colliders:
                x, y, w, h = c.rect.pos.x, c.rect.pos.y, c.rect.size[0], c.rect.size[1] 
                lines = [
                    [x, y, x, y+h], 
                    [x, y, x+w, y],
                    [x+w, y, x+w, y+h],
                    [x, y+h, x+w, y+h],
                ]
                for line in lines:
                    point = collide_line_with_line(ray, line)
                    if point == Vector2():
                        continue
                    new_len = (point - Vector2(ray[0], ray[1])).length() 
                    if new_len < min_len:
                        min_len = new_len 
                        min_len_point = point
            return min_len_point

        radius = 1500
        loop_amount = 11
        # raycast within view
        points = []
        empty_vector = Vector2()
        for i in range(0, loop_amount):
            t = i/loop_amount
            ray_direction = learp(self.right, self.left, t)
            x1, y1 = self.ecenter
            x2, y2 = self.ecenter + ray_direction * radius
            r=  (x1, y1, x2, y2)

            point = collide_ray_with_rect(r, colliders)
            if point != empty_vector:
                points.append(point)
        self.points = points

        pos = self.hitbox.rect.pos
        tile_size = (32, 32) # hardcoded but meehh
        
        x, y = pos.x, pos.y 
    
        px, py, pw, ph = self.path[self.current_index]
        pcx, pcy = px + pw/2, py + ph/2 

        delta = Vector2(x, y) - Vector2(pcx, pcy) 
        delta.x = int(delta.x)
        delta.y = int(delta.y)

        if delta == Vector2():
            self.current_index += 1
            if self.current_index >= len(self.path):
                self.current_index = 0
        else:
            direction = -delta.normalize() 
            self.velocity = direction * 130 * dt 
        
            
    def get_colliders(self , colliders):
        collided = []
        for collider in colliders:
            if self.hitbox.collide(collider):
                collided.append(collider)
        
        return collided

    def set_path(self, path):
        self.path = path

    def move(self , colliders):

        self.hitbox.rect.x += self.velocity.x
        # movement towards a predefined path

        # calc position in map ceil no floor

        # move towards next position


        rect = self.hitbox.rect
        x, y = rect.pos + rect.size/2
        print(x, y)

        # collision detection
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
        


   
    def display_light(self , surface : pygame.Surface , offset=pygame.Vector2(0,0)):
        light_size = pygame.Vector2([self.view_distance*2]*2)
        light_offset = offset - (self.rect.size / 2 - light_size / 2)
        surface.blit(self.light , [self.rect.x - light_offset.x , self.rect.y - light_offset.y], special_flags=BLEND_RGB_ADD)
    
    def display(self , surface : pygame.Surface , offset : pygame.Vector2):
        text_pos = self.hitbox.rect.pos - self.hitbox_offset - offset
        surface.blit(self.texture , text_pos)

        self.ecenter -= offset
        pygame.draw.line(surface, (0, 0, 255),self.ecenter, self.ecenter+ self.right*self.view_distance)
        pygame.draw.line(surface, (0, 0, 255),self.ecenter, self.ecenter+ self.left*self.view_distance)
        self.points = [point-offset for point in self.points]
        self.points.append(self.ecenter)


        if len(self.points) >= 2:
            pygame.draw.polygon(surface, (255, 0, 0), self.points, 2)

        for point in self.points:
            pygame.draw.circle(surface, (0, 0, 255), point, 3, 3)

