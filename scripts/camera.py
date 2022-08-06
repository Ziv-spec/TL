import pygame

from pygame.locals import *
from scripts.form import *

class Camera():
     
     def __init__(self , pos , size):
          self.pos = pygame.math.Vector2(pos)
          self.size = pygame.math.Vector2(size)
          self.render_surf = pygame.Surface(self.rect.size)
     
     @property
     def rect(self):
          return FloatRect(self.pos , self.size)
     
     def erase_surf(self , color):
          self.render_surf.fill(color)
     
     def update(self , dt , max_fps=60):
          if (self.render_surf.get_width() != self.size.x or self.render_surf.get_height() != self.size.y):
               self.render_surf = pygame.Surface(self.rect.size)
     
     def display(self , screen , display_rect : Rect):
          screen.blit(pygame.transform.scale(self.render_surf , display_rect.size) , [display_rect.x , display_rect.y])
               
          