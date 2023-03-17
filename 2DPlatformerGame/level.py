from os import kill
import pygame
from player import Player
from tiles import Tile, AnimatedTile, Coin,Diamond
from settings import *
from particles import ParticleEffect
from enemy import Enemy
from game_data import levels
from math import sin

class Level:
    def __init__(self,level_data,surface,current_level,create_overworld,change_coins,change_health):
        
        self.display_surface = surface
        self.current_level = current_level
        level_data2 = levels[current_level]
        self.new_max_level = level_data2['unlock']
        self.create_overworld = create_overworld
        
        self.setup_level(level_data)       
        self.world_shift = 0
        self.current_x = 0
        self.current_y = 0
        
        self.change_coins = change_coins
        self.change_health = change_health
        self.invincible = False
        self.invincibility_duration = 600
        self.hurt_time = 0
        
        
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        
        
        self.explosion_sprites = pygame.sprite.Group()
        
        

    
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.create_overworld(self.current_level,self.new_max_level)
        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level,0)

    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -=pygame.math.Vector2(10,5)
        else:
            pos +=pygame.math.Vector2(10,-5)  
            
        
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)
        
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False    
    
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom-offset,'land')
            self.dust_sprite.add(fall_dust_particle)
            
            
    def setup_level(self,layout):
        self.tiles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.constraints = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.diamond = pygame.sprite.Group()
        for row_index,row in enumerate(layout):
            for col_index,cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == 'X':
                    tile = Tile(x,y,tile_size)
                    self.tiles.add(tile)
                if cell == 'P':
                    player_sprite = Player(x,y, self.display_surface,self.create_jump_particles)
                    self.player.add(player_sprite)
                if cell == 'E':
                    sprite = Enemy(x,y,tile_size,"./graphics/enemy/run")
                    self.enemies.add(sprite)
                if cell == '|':
                    sprite = Tile(x,y,tile_size)
                    self.constraints.add(sprite)
                if cell == 'C':
                    coin = Coin(x,y,32,".\graphics\coin")
                    self.coins.add(coin)
                if cell == 'F':
                    diamond = Diamond(x,y,32)
                    self.diamond.add(diamond)  
     
    def  scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width/3 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > (screen_width/3)*2 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 4
    
    def horizontal_movement_collision(self):
        player = self.player.sprite
        
        player.rect.x += player.direction.x * player.speed
        
               
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >=0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <=0):
            player.on_right = False

    def collect_coins(self):
        player = self.player.sprite
        
        player.rect.x +=player.direction.x * player.speed
        
        for sprite in self.coins.sprites():
            if sprite.rect.colliderect(player.rect):
                self.change_coins(1)
                self.coins.remove(sprite)
            
    def get_damage(self):
        if not self.invincible:
            self.change_health(-10)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()
    
    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False
                
    
    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False
              
    def enemy_moves(self):
        for enemy in self.enemies.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraints.sprites(),False):
                enemy.reverse()
            if  pygame.sprite.collide_rect(enemy, self.player.sprite) and self.invincible is False:
                enemy.reverse()
                
    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemies,False)
        
        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom 
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center,'explosion')
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.get_damage()
    
    def check_fall_damage(self):
        self.current_y = self.player.sprite.rect.top
        if self.current_y > 1000:
            self.get_damage()
        
    def level_finish(self):
        player = self.player.sprite
        
        player.rect.x +=player.direction.x * player.speed
        
        for sprite in self.diamond.sprites():
            if sprite.rect.colliderect(player.rect):
                self.create_overworld(self.current_level,self.new_max_level)
                
              
    def run(self):
        self.input()
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.coins.update(self.world_shift)
        self.coins.draw(self.display_surface)
        self.diamond.update(self.world_shift)
        self.diamond.draw(self.display_surface)
        self.scroll_x()
        
              
        self.player.update()
        self.collect_coins()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.player.draw(self.display_surface)
        self.invincibility_timer()
        self.check_enemy_collisions()
        self.check_fall_damage()
        
        
        self.enemies.update(self.world_shift)
        self.constraints.update(self.world_shift)
        self.enemy_moves()
        self.enemies.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)
        
        self.level_finish()
        