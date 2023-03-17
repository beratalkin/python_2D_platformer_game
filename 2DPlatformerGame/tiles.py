import pygame
from support import import_folder

class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.image.fill('#3A160E')
        self.rect = self.image.get_rect(topleft = (x,y))
    
    def update(self, x_shift):
        self.rect.x += x_shift
        
class AnimatedTile(Tile):
    def __init__(self, x,y, size, path):
        super().__init__(x,y,size)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        
    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift

class Coin(AnimatedTile):
    def __init__(self, x,y, size, path):
        super().__init__(x,y, size, path)
        center_x = x + int(size/2)
        center_y = y + int(size/2)
        self.rect = self.image.get_rect(center = (center_x,center_y))
        
class Diamond(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()      
        img = pygame.image.load(".\graphics\diamond\diamond.png")
        self.image = img
        self.rect = self.image.get_rect(center=(x,y))
        
    def update(self, x_shift):
        self.rect.x += x_shift
        
        