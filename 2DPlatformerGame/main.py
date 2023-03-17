from re import S
import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI
from pygame import mixer

class Game:
    def __init__(self):
        
        self.max_level =  0
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0
        
        self.overworld = Overworld(0,self.max_level,screen,self.create_level)
        self.status='overworld'
        
        self.ui = UI(screen)
    
    def create_level(self,current_level):
        if current_level == 0:   
            self.level = Level(level_map0,screen,current_level,self.create_overworld,self.change_coins,self.change_health)
        if current_level == 1:
            self.level = Level(level_map1,screen,current_level,self.create_overworld,self.change_coins,self.change_health)   
        if current_level == 2:
            self.level = Level(level_map0,screen,current_level,self.create_overworld)
        
        self.status = 'level'
    
    def create_overworld(self,current_level,new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level,self.max_level,screen,self.create_level)
        self.status = 'overworld'
        
    def change_coins(self,amount):
        self.coins += amount
    
    def change_health(self,amount):
        self.cur_health += amount
        
    def check_dead(self):
        if self.cur_health <= 0:
            self.cur_health=100
            self.coins=0
            self.max_level
            self.overworld = Overworld(0,self.max_level,screen,self.create_level)
            self.status='overworld'
    
    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        elif self.status == 'level':
            self.level.run()
            self.ui.show_health(self.cur_health,self.max_health)   
            self.ui.show_coins(self.coins)
            self.check_dead()

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
mixer.music.load('./music/bg.mp3')
mixer.music.set_volume(0.05)
mixer.music.play(-1)

print("Press Spacebar to enter a map.")

while True:
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('#C3976A')
    game.run()
    pygame.display.update()
    clock.tick(60)