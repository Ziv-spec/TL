import os
import pygame
import json

from xml.etree.ElementTree import *
from pygame.locals import *
from scripts.particles import *
from scripts.form import *
from scripts.camera import *
from math import *
from copy import *
from random import *
from scripts.unclassed_functions import *

def load_tileset(tsx_path):
     parsed = parse(tsx_path)
     root = parsed.getroot()
     tile_size = [int(root.get("tilewidth")),int(root.get("tileheight"))]
     t1_path = root[0].get("source")
     image = pygame.image.load(os.path.join(os.path.dirname(tsx_path) , t1_path))
     image_size = [int(root[0].get("width")) , int(root[0].get("height"))]

     tiles = []
     
     i = 1
     for y in range(0 , image_size[1] // tile_size[1]):
          
          for x in range(0 , image_size[0] // tile_size[0]):
               tile = image.subsurface(Rect(x*tile_size[0],y*tile_size[1],tile_size[0],tile_size[1]))
               tiles.append(tile)
               i+=1

     
     return tiles , tile_size[0]

def get_objects(root : Element):
     
     object_group = root.find("objectgroup")

     obj_list = {}
     
     def get_key(attributes):
          
          if "name" in attributes.keys():
               name = attributes.pop("name")
               return name
          else:
               id = attributes.pop("id")
               return id
     
     for obj in object_group.findall("object"):
          properties = obj.find("properties")
          prop_datas = {}
          if properties:
               for p in properties:
                    attribs = p.attrib
                    key = get_key(attribs)
                    prop_datas[key] = attribs
          
          attribs = obj.attrib
          key = get_key(attribs)
          if not key in obj_list.keys():
               obj_list[key] = attribs|prop_datas
          elif not isinstance(obj_list[key] , list):
               datas = obj_list[key]
               new_datas = [datas , attribs|prop_datas]
               obj_list[key] = new_datas
          else:
               obj_list[key].append(datas)
          
     
     return obj_list

class TileMap():
     
     def __init__(self , chunk_size=[4,4]):
          
          self.tileset = []
          self.size = [0,0]
          self.collider_chunks = {}
          self.layers = {}
          self.chunk_size = chunk_size
          self.tilesize = 0
          
     def get_collider_by_data(self , pos):
          
          rect = FloatRect(pos , pygame.Vector2(self.tilesize))
          
          return Collider(rect , "block")
          
     def load_map(self , map_path):
          root = parse(map_path).getroot()
          self.tileset , self.tilesize = load_tileset(os.path.join(os.path.dirname(map_path) , root.find("tileset").get("source")))
          self.size[0] = int(root.get("width"))
          self.size[1] = int(root.get("height"))
          
          layer_datas = {}
          self.object_datas = get_objects(root)
          
          for k ,  obj in self.object_datas.items():
               if "chest" in k:
                    tid = obj.pop("gid")
                    obj["texture"] = self.tileset[int(tid)-1]
          
          for layer in root.findall("layer"):
               data = layer.find("data").text
               data = data.strip("\n").splitlines()
               t_tab = []
               
               for line in data:
                    l = line.strip(",").split(",")
                    t_tab.append(l)
               
               layer_datas[layer.get("name")] = t_tab
          
          # iteration through layers
          for key in layer_datas:
               t_tab = layer_datas[key]
               # specific process with the layer for colliders
               if key == "colliders":
                    for cy in range(0 , self.size[1] // 4):
                         for cx in range(0 , self.size[0] // 4):
                              c_chunk = []
                              pos = f"{cx},{cy}"
                              for y in range(cy*4 , (cy+1)*4):
                                   # print(y)
                                   for x in range(cx*4 , (cx+1)*4):
                                        if (t_tab[y][x] == "69"):
                                             collider = self.get_collider_by_data(pygame.Vector2(x*self.tilesize , y*self.tilesize))
                                             c_chunk.append(collider)   
                              if c_chunk != []:
                                   self.collider_chunks[pos] = c_chunk
               else:
                    layer_data = {}
                    for cy in range(0 , self.size[1] // self.chunk_size[1]):
                         for cx in range(0 , self.size[0] // self.chunk_size[0]):
                              chunk_surf = pygame.Surface([self.tilesize*self.chunk_size[0] , self.tilesize*self.chunk_size[1]] , SRCALPHA)
                              pos = f"{cx},{cy}"
                              py = 0
                              for y in range(cy*self.chunk_size[1] , (cy+1)*self.chunk_size[1]):
                                   px = 0
                                   for x in range(cx*self.chunk_size[0] , (cx+1)*self.chunk_size[0]):
                                        if (t_tab[y][x] != "0"):
                                             chunk_surf.blit(self.tileset[int(t_tab[y][x])-1] , [px*self.tilesize , py*self.tilesize])
                                   
                                        px += 1
                                   py += 1
                              layer_data[pos] = chunk_surf  
                    self.layers[key] = layer_data
          
          # print(self.chunks)

     def display(self , surface , offset=pygame.Vector2(0,0)):
          
          for layer in self.layers.values():
               for key , chunk in layer.items():
                    pos = [int(val) for val in key.split(",")]
                    surface.blit(chunk , [(pos[0]*self.chunk_size[0]*self.tilesize-offset.x) , (pos[1]*self.chunk_size[1]*self.tilesize-offset.y)])
                         
     

class Tile():
     
     def __init__(self , pos , surface):
          self.pos = pos
          self.surface = surface