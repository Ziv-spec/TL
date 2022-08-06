import pygame


from scripts.form import *
from pygame.locals import *


class Player:
    
    def __init__(self , hitbox : Collider):
        
        self.hitbox = hitbox
        self.hitbox_offset = pygame.Vector2(0,0)
        
        self.velocity = pygame.Vector2(0,0)
        self.km = {"right":False , "left":False , "up":False , "down":False}
        self.directions = {"right":1 , "left":-1 , "up":-1 , "down":1}
        self.angle = 0
    
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
        self.velocity = result * 100 * dt
    
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
        
        self.hitbox.rect.draw(surface , offset , True)
        
        