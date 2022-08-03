import pygame 
from collections import defaultdict
from os.path import getmtime
from os import stat
import platform
from pygame import Vector2

# TODO: 
#  - make tile selection tool thingy
#  - undo-redo system  
#  - ui system? probably imgui or something of the like, very simple for specific thigns  
#  - text system (just have text wrap, and the likes)
#  - beginning of combat system tomorrow
#  - make settings even more robust
#  - make chunck system for tiles

# DONE: 
#  - camera to go around the world freely and edit things

# for undo and redo
class CircleBuffer:
  def __init__(self, buff_size):
    self.begin = 0 
    self.end   = 0
    self.buff_size = buff_size
    self.buff = [0]*buff_size
  
  def next(self):
    end = (self.end + 1) % self.buff_size
    if end != self.begin:
      self.end = end

  def previous(self):
    end = (self.end - 1 + self.buff_size) % self.buff_size
    if end != self.begin:
      self.end = end  

  def get_next(self):
    value = self.buff[self.end]
    self.next()
    return value

  def get_previous(self):
    value = self.buff[self.end]
    self.previous()
    return value

  def set_next(self, item):
    self.buff[self.end] = item
    self.next()

  def set_previous(self, item):
    self.buff[self.end] = item
    self.previous()

class Context: 
  def __init__(self, display, events):
    self.display = display 
    self.settings = defaultdict(lambda: False)  # rethink this
    self.undo_buffer = CircleBuffer(256)

    self.events = events 
    self.events_processed = defaultdict(lambda: False) 
    self.dt = 0
    self.world = [[0]*100 for i in range(100)]
    self.camera = Vector2()
    self.tile_size = (32, 32)


def load_settings(path, settings):

  def eat_trash(line, begin_index):
    for j in range(begin_index, len(line)):
      if line[j] != ' ' or line[j] != '\t' or line[j] != '\r':
        return j
    return max(len(line)-1, 0)
  
  def error(msg, path, line):
    print(path + ":", msg, f"at {line}")
    
  with open(path, 'rt') as f:
    data = f.read()
    lines = data.split("\n")
    for i, line in enumerate(lines):
      
      if len(line) == 0:
        continue
      
      keyword = ""
      end = len(line) 
      begin = eat_trash(line, 0)
      for j in range(begin, len(line)):
        if line[j].isalpha() or line[j] == '_' or line[j].isdecimal():
          keyword += line[j]
        else: 
          end = j+1
          break

      begin = eat_trash(line, end)
      if line[begin] != '=':
        error("error expected assignment of value", path, i)
        return False

      value = None 
      end = begin + 1
      begin = eat_trash(line, end)
      if line[begin+1].isdigit():
        value = float(line[begin+1:])
      else: 
        error("not implemented value support", path, i)
        return False

      settings[keyword] = value
  
  return True

def main():


  size = (800, 600) # TODO: check which window size is acceptabe
  running = True
  FPS =  60
  clock  = pygame.time.Clock()
  display: pygame.Surface = pygame.display.set_mode(size)
  bg_color = (255, 255, 255) 

  context = Context(display, None)

  modified_date, last_modified_date = None, None
  settings_file_path = "data/settings.txt"

  dt = 1/FPS
  while running:

    display.fill(bg_color)
    context.events = pygame.event.get()
    context.dt = dt

    # find the modified date of the settings file 
    if platform.system() == "Windows": modified_date = getmtime(settings_file_path)
    else: modified_date = stat(settings_file_path).st_mtime

    if last_modified_date != modified_date:
      success = load_settings(settings_file_path, context.settings)
      if not success: 
        print("NOTE: could not load all settings, some things might break.")


    # TODO: context switch whenever needed system
    running = editor(context)
    if not running: 
      return

    pygame.display.update()
    last_modified_date = modified_date
    dt = clock.tick(FPS) * 0.001


def editor(context: Context) -> bool:

  tile_size = context.settings['tile_size']
  tile_size = (int(tile_size), int(tile_size))
  tile_surf = pygame.Surface(tile_size)
  dt = context.dt

  def screen_to_world_space(context, screen_pos):
    tile_width, tile_height = context.tile_size
    cx, cy = context.camera 
    return (screen_pos[0]-cx)//tile_width, (screen_pos[1]-cy)//tile_height

  mouse = pygame.mouse.get_pos()
  cursor_position = screen_to_world_space(context, mouse) 

  for event in context.events:
    if event.type == pygame.QUIT:
      pygame.quit() # de-initialize pygame resources
      return False
    if event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        context.events_processed['left_click'] = True
    if event.type == pygame.MOUSEBUTTONUP:
      if event.button == 1:
         context.events_processed['left_click'] = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        context.events_processed['a'] = True
      elif event.key == pygame.K_w:
        context.events_processed['w'] = True
      elif event.key == pygame.K_s:
        context.events_processed['s'] = True
      elif event.key == pygame.K_d:
        context.events_processed['d'] = True
      elif event.key == pygame.K_z:
        last_action = context.undo_buffer.get_previous()
      elif event.key == pygame.K_y:
        context.undo_buffer.get_next()

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        context.events_processed['a'] = False
      elif event.key == pygame.K_w:
        context.events_processed['w'] = False
      elif event.key == pygame.K_s:
        context.events_processed['s'] = False
      elif event.key == pygame.K_d:
        context.events_processed['d'] = False
      
  
  v = 300
  x, y = v*dt, v*dt
  context.camera += Vector2(-context.events_processed['a']*x + context.events_processed['d']*x, -context.events_processed['w']*y + context.events_processed['s']*y)
      
  if context.events_processed['left_click']:
    context.world[int((mouse[0]+context.camera[0])//tile_size[0])][(int(mouse[1]+context.camera[1])//tile_size[1])] = 1
  context.display.blit(tile_surf, (int((mouse[0]//tile_size[0])*tile_size[0]), int((mouse[1]//tile_size[1])*tile_size[1])))

  for i, line in enumerate(context.world):
    for j, tile in enumerate(line):
      if tile == 1:
        context.display.blit(tile_surf, (round(i*tile_size[0]-context.camera[0]), round(j*tile_size[1]-context.camera[1])))

  return True 



import time
if __name__ == "__main__":
  start = time.time()
  pygame.init() # TODO: check whether I need this
  print(time.time() - start)

  main()



