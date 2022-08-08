import pygame

from scripts.animation import *
from scripts.form import *
from scripts.unclassed_functions import mult_image
from pygame.locals import *


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
        self.v = pygame.Vector2()

        self.texture = pygame.Surface((16, 16))
        self.texture.fill((255, 0, 0)) # red
        self.velocity = pygame.Vector2()
        self.view_angle = 80 # in degrees
        self.view_distance = 150

        self.direction = pygame.Vector2(0 , 1)
        self.colliders = None
        
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

    def update(self, dt, colliders):
        self.colliders = colliders
        
        # construct enemy view 
        ewidth, eheight = self.hitbox.rect.size
        self.ecenter = pygame.Vector2(self.hitbox.rect.x+ewidth//2, self.hitbox.rect.y+eheight//2)

        # view_angle_radians = self.view_angle*pi/180
        # direction_in_radians = 0
        # if self.direction.x != 0:
        #     direction_in_radians = atan(self.direction.y / self.direction.x)

        #direction angle
        da = pygame.Vector2(self.direction.x , -self.direction.y).angle_to(pygame.Vector2(0))
        
        self.right , self.left = pygame.Vector2(cos(radians(da+self.view_angle/2)),-sin(radians(da+self.view_angle/2))),pygame.Vector2(cos(radians(da-self.view_angle/2)),-sin(radians(da-self.view_angle/2)))

        loop_amount = 10

        points = []
        empty_vector = pygame.Vector2()
        for i in range(0, loop_amount):
            t = i/loop_amount
            ray_direction = learp(self.right, self.left, t)
            x1, y1 = self.ecenter
            x2, y2 = self.ecenter + ray_direction * self.view_distance
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
        
        