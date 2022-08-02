from genericpath import getmtime
import pygame 
from collections import defaultdict

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
    self.next(self)
    return self.buff[self.end]

  def get_previous(self):
    self.previous(self)
    return self.buff[self.end]

  def set_next(self, item):
    self.next(self)
    self.buff[self.end] = item

  def set_previous(self, item):
    self.previous(self)
    self.buff[self.end] = item

class Context: 
  def __init__(self, display, events):
    self.display = display 
    self.settings = defaultdict(lambda: False)  # rethink this

    self.events = events 
    self.events_processed = defaultdict(lambda: False) 

# globals 
world = [[0]*100 for i in range(100)]

from os.path import getmtime
from os import stat
import platform

def main():
  size = (800, 600) # TODO: check which window size is acceptabe
  running = True
  FPS = 120 
  clock  = pygame.time.Clock()

  display: pygame.Surface = pygame.display.set_mode(size)
  bg_color = (255, 255, 255) 

  context = Context(display, None)

  modified_date, last_modified_date = None, None
  settings_file_path = "data/settings.txt"
  load_settings(settings_file_path, context.settings)


  while running:

    display.fill(bg_color)
    context.events = pygame.event.get()

    # find the modified date of the settings file 
    if platform.system() == "Windows": modified_date = getmtime(settings_file_path)
    else: modified_date = stat(settings_file_path).st_mtime

    if last_modified_date != modified_date:
      load_settings(settings_file_path, context.settings)


    # TODO: context switch whenever needed system
    running = editor(context)
    if not running: 
      return

    pygame.display.update()
    last_modified_date = modified_date
    clock.tick(FPS)

def load_settings(path, settings):

  with open(path, 'rt') as f:
    data = f.read()
    lines = data.split("\n")
    for i, line in enumerate(lines):
      words = line.split(" ")
      if len(words) == 3:
        name, operation, value = words
        if not name.isalpha():
          print(f"invalid var name on line {i}")
          return False 
        if operation != '=':
          print(f"invalid opeartion on line {i}")
          return False 
        if not value.isnumeric(): 
          print(f"invalid value is not numeric on line {i}")
          return False 
        settings[name] = int(value)
      elif len(words) == 1 and words[0] == '':
        pass
      else: 
        print(f"unexpected word amount {len(words)} on line {i}")

def editor(context: Context) -> bool:
  global world

  tile_size = (32,32) 
  tile_surf = pygame.Surface(tile_size)

  def screen_to_world_space(screen_pos, tile_size):
    return (screen_pos[0]//tile_size[0], screen_pos[1]//tile_size[1])

  mouse = pygame.mouse.get_pos()
  cursor_position = screen_to_world_space(mouse, tile_size) 

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
      
  if context.events_processed['left_click']:
    world[cursor_position[0]][cursor_position[1]] = 1

  context.display.blit(tile_surf, (cursor_position[0]*tile_size[0], cursor_position[1]*tile_size[1]))

  for i, line in enumerate(world):
    for j, tile in enumerate(line):
      if tile == 1:
        context.display.blit(tile_surf, (i*tile_size[0], j*tile_size[1]))

  return True 



import time
if __name__ == "__main__":
  start = time.time()
  pygame.init() # TODO: check whether I need this
  print(time.time() - start)

  main()



