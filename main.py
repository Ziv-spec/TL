import pygame 



def main():
  size = (800, 600) # TODO: check which window size is acceptabe
  running = True
  FPS = 120 
  clock  = pygame.time.Clock()

  display: pygame.Surface = pygame.display.set_mode(size)
  bg_color = (255, 255, 255) 

  while running:

    # Event loop
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

    # drawing
    display.fill(bg_color)
    pygame.display.update()
    clock.tick(FPS)

import time
if __name__ == "__main__":
  start = time.time()
  pygame.init() # TODO: check whether I need this
  print(time.time() - start)
  main()



