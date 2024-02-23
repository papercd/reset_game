#alright, so this is where I am going to implement physics for the objects 
#of my game. 
import random
import pygame 
from scripts.particles import Particle
from scripts.health import HealthBar,StaminaBar
from scripts.indicator import indicator 

class PhysicsEntity:
   
    def __init__(self,game,e_type,pos,size):
        self.game = game 
        self.type = e_type 
        self.pos = list(pos)  #this list() ensures that the position variable that you pass to the constructor 
                              #becomes a list. This gives us flexibility with passing argumments here for example 
                              #when we pass a tuple, this allows us to actually manage the position variable, as tuples can't be modified after initialization.
        self.collisions = {'up' :False,'down' : False, 'left': False, 'right': False }
        self.size = size
        self.velocity = [0,0]
        self.state = ''
        self.anim_offset = (-0,-0)
        self.flip = False
        self.set_state('idle')
        self.cut_movement_input = False 


    def set_state(self,action):
        if action != self.state: 
            self.state = action 
            self.animation = self.game.assets[self.type + '/' + self.state].copy() 

    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
    
    def update_pos(self, tile_map, movement = (0,0)):
        
        self.collisions = {'up' :False,'down' : False, 'left': False, 'right': False }
        
        self.velocity[1] = min(5,self.velocity[1] +0.2)

        if self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0]+0.25, 0)  
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] -0.25,0)

         

        if self.cut_movement_input:
            frame_movement = (self.velocity[0],self.velocity[1])
        else: 
            frame_movement =  (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

    
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect() 
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: 
                    self.collisions['right'] = True
                    entity_rect.right = rect.left 
                if frame_movement[0] < 0: 
                    self.collisions['left'] = True
                    entity_rect.left = rect.right 
                self.pos[0] = entity_rect.x 
        



        self.pos[1] += frame_movement[1]
        entity_rect = self.rect() 
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0: 
                    self.collisions['down'] = True
                    entity_rect.bottom = rect.top  
                if frame_movement[1] < 0:  
                    self.collisions['up'] = True
                    entity_rect.top = rect.bottom
                self.velocity[1] = 0 
                self.pos[1] = entity_rect.y 

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0 :
            self.flip = True 

        self.animation.update()



    def render(self,surf,offset):
        
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip, False),(self.pos[0]-offset[0]+self.anim_offset[0],self.pos[1]-offset[1]+self.anim_offset[1]))
        


class Enemy(PhysicsEntity):
    def __init__(self,game,pos,size,variant):
        super().__init__(game,variant,pos,size)
        self.walking = 0
        self.air_time =0
        
    def set_state(self,action):
        if action != self.state: 
            self.state = action 
            self.animation = self.game.enemies[self.type + '/' + self.state].copy() 

class Canine(Enemy):
    def __init__(self,game,pos,size,color):
        self.color = color 
        self.aggro = False 
        self.hit_mask = None
        self.first_hit = False


        super().__init__(game,pos,size,'Canine')

        self.health = 53
        self.health_bar = HealthBar(self.pos[0],self.pos[1],20,2,self.health)
        
    def collision_rect(self):
        return pygame.Rect(self.pos[0]+3,self.pos[1]+4,self.size[0]-6,self.size[1]-8)


    def set_state(self,action):
        if action != self.state: 
            self.state = action 
            self.animation = self.game.enemies[self.type + '/' + self.color  + '/'+ self.state].copy() 

    def update(self,tilemap,movement = (0,0)):
        
        self.path = tilemap.grounded_enemeis_return_path(self.pos,self.size,self.flip,False)
        #now I want to make the AI of the enemies a bit better 
        
        self.air_time +=1
        if self.health >= 0: 
            if self.aggro: 
                #when it's supposed to chase the player. 
                pass 
            else: 
                
                if self.walking :
                    
                    if tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8)):
                        if tilemap.solid_check((self.pos[0] + (-8 if self.flip else 8+self.size[0]),self.pos[1]+8-tilemap.tile_size)):
                            if tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0] ),self.pos[1]+8-tilemap.tile_size*2)):
                                self.flip = not self.flip 
                            else: 
                                self.velocity[1] = -5
                                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                        else: 
                            
                            self.velocity[1] = -3.3
                            movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                    else:
                        if tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8-tilemap.tile_size)):
                            if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8-tilemap.tile_size*2)):
                                
                                self.velocity[1] = -5
                                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                            else: 
                                self.flip = not self.flip 
                                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                        else: 
                            if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8+tilemap.tile_size)):
                                if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8+tilemap.tile_size*2)):
                                    if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8+tilemap.tile_size*3)):
                                        if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8+tilemap.tile_size*4)):
                                            if not tilemap.solid_check((self.pos[0]+ (-8 if self.flip else 8+self.size[0]),self.pos[1]+8+tilemap.tile_size*5)):
                                                self.flip = not self.flip 
                                            else: 
                                                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                                        else: 
                                            movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                                    else: 
                                        movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                                else: 
                                    movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                            else: 
                                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                            
                    self.walking = max(0, self.walking - 1)
                
                elif random.random() < 0.01:
                    #things to do when you aren't walking 
                    
                    self.walking = random.randint(30,120)

        #update health bar 
        self.health_bar.x = self.pos[0] + 5
        self.health_bar.y = self.pos[1] -5
        self.health_bar.cur_resource = self.health

        super().update_pos(tilemap,movement=movement)
        
        if self.health <= 0 :
            if self.collisions['down']:
                self.set_state('grounded_death')
            """
            if self.air_time > 4:
                if self.velocity[1] < 0:
                    self.set_state('airborne_death_up')
            
                elif self.velocity[1] >0:
                    self.set_state('airborne_death_down')
            """
            if self.animation.done: 
                del self 
                return True 
        else: 
            if self.collisions['down']:
                self.air_time = 0
        
            if self.air_time > 4:
                
                if self.velocity[1] < 0:
                    self.set_state('jump_up')
            
                elif self.velocity[1] >0:
                    self.set_state('jump_down')
                
            elif movement[0] != 0:
                self.set_state('run')    
            else: 
                self.set_state('idle') 

       
            return False 
            
        
        
    def render(self,surf,offset):
        if self.first_hit:
            self.health_bar.render(surf,offset)
        if self.hit_mask:
            for offset_ in [(-1,0),(1,0),(0,-1),(0,1)]:
                surf.blit(self.hit_mask.to_surface(unsetcolor=(0,0,0,0),setcolor=(255,255,255,255)),(self.pos[0] - offset[0]+offset_[0],self.pos[1]-offset[1]+offset_[1]))
            self.hit_mask = None
        super().render(surf,offset=offset)

        #also render the hit mask 
        #pathfinding testing
        """
        test_surf = pygame.Surface((2,2))
        test_surf.fill((180,0,0,255))
        surf.blit(test_surf,(self.pos[0]+self.size[0] + (-8 if self.flip else 8) -offset[0], self.pos[1]- offset[1]))
        """
        # (self.pos[0]+self.size[0] + (-8 if self.flip else 8),self.pos[1]//16-tilemap.tile_size)
        """
        if self.path: 
            
            for loc in self.path: 
                test_surf = pygame.Surface((2,2))
                test_surf.fill((180,0,0,255))
                surf.blit(test_surf,(loc[0] -offset[0],loc[1] - offset[1]))
        """
    
    def hit(self,hit_damage):
        self.health -= hit_damage
        self.first_hit = True
        self.hit_mask = pygame.mask.from_surface(self.animation.img() if not self.flip else pygame.transform.flip(self.animation.img(),True,False))
        
    
        
        
class PlayerEntity(PhysicsEntity):
    def __init__(self,game,pos,size):
        #attributes required to implement weapon equipment 
        self.equipped = False 
        self.cur_weapon = None 

    

        super().__init__(game,'player',pos,size)

        self.recov_rate = 0.6
        self.stamina = 100
        self.health = 200

        self.health_bar = HealthBar(32,300,200,4,self.health)
        self.stamina_bar =  StaminaBar(32,310,98,4,self.stamina)

        self.health_UI = self.game.assets['health_UI']
        self.stamina_UI = self.game.assets['stamina_UI']

        self.jump_count = 2
        self.wall_slide = False
        self.slide = False 
        self.on_wall = self.collisions['left'] or self.collisions['right']
        self.air_time = 0
      
        self.is_shooting = False

        #attributes required to implement double tap 
      
        self.timer= False 
        self.time = 0

        self.fatigued = False 
        self.running = False 
        

        
        
       
    def set_state(self,action):
        if action != self.state: 
            self.state = action 
            self.animation = self.game.assets[self.type + '/' + ('holding_gun/' if self.equipped else '') + self.state].copy() 

    def update_pos(self, tile_map,cursor_pos,movement=(0, 0)):
        
        new_movement = [movement[0],movement[1]]

        
        if self.fatigued: 
            self.recov_rate = 0.3
            new_movement[0] *= 0.5
            if self.stamina >= 80:
                self.fatigued = False 
        else: 
            self.recov_rate = 0.6
            if self.running: 
                if self.stamina >= 10:
                    #then you can run. 
                    if movement[0] != 0:
                        self.stamina -= 1.2
                        new_movement[0] *= 1.4
                else: 
                    new_movement[0] *= 0.5
                    self.fatigued = True 
            else: 
                if self.stamina < 10: 
                    new_movement[0] *= 0.5
                    self.fatigued = True 
            
        super().update_pos(tile_map, new_movement)


        #every frame, the stamina is increased by 0.7
        

        self.stamina = min(100, self.stamina + self.recov_rate)
        self.air_time +=1
        
        self.time += self.timer 

        self.cut_movement_input = False 

        if self.collisions['down']:
            self.jump_count =2 
            self.air_time = 0
            
            
        self.wall_slide = False
        self.on_wall = self.collisions['left'] or self.collisions['right']
        

        if self.on_wall and self.air_time > 4:
            self.wall_slide = True 
            self.velocity[1] = min(self.velocity[1],0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True 
            
            self.set_state('wall_slide')
        
        if not self.wall_slide: 
            if self.air_time > 4:
                self.boost_on_next_tap = False 
                if self.velocity[1] < 0:
                    self.set_state('jump_up')
                elif self.velocity[1] >0:
                    self.set_state('jump_down')
               
            elif movement[0] != 0:
                if self.fatigued: 
                    self.set_state('walk')
                else: 
                    self.set_state('run')
                if self.slide:
                    self.cut_movement_input = True
                    self.set_state('slide')
                    
            else: 
               
                self.set_state('idle') 
            

        if self.equipped:
            self.cur_weapon.update(cursor_pos)
        
        #update the health and stamina bars 
        self.health_bar.cur_resource = self.health
        self.stamina_bar.cur_resource = self.stamina

    def accel(self):
        #check the stamina and return the speed. 
        if self.fatigued: 
            if self.stamina <= 70:
                return 1
            else: 
                self.fatigued = False 
                self.stamina -= 1.3
                return 2.3
        else: 
            if self.stamina > 10:
                self.stamina -= 1.3
                return 2.3
            else: 
                self.fatigued = True 
                return 1
        
        
    
    def render(self,surf,offset):
        super().render(surf,offset)

        #render the health bar and the stamina bar 
        #add scaling later so that the health and stamina bars can dynamically change. 
        surf.blit(self.health_UI,(self.health_bar.x-2,self.health_bar.y-2)) 
        self.health_bar.render(surf,(0,0))

        surf.blit(self.stamina_UI,(self.stamina_bar.x-2,self.stamina_bar.y-2)) 
        self.stamina_bar.render(surf,(0,0))

        #optimize health bar indicator rendering by creating an update function for the indicators 

        #render the health bar indicator 
        health_ind = indicator(int(self.health_bar.cur_resource),int(self.health_bar.max_resource))
        health_ind.render(self.health_bar.x + 84,self.health_bar.y-1,surf)
        
        #render the stamina bar indicator 
        stamina_ind = indicator(int(self.stamina_bar.cur_resource),int(self.stamina_bar.max_resource))
        stamina_ind.render(self.stamina_bar.x+34,self.stamina_bar.y-1,surf)

        if self.equipped: 
            self.cur_weapon.render(surf,offset)
    
    def dash(self):
        if not self.fatigued: 
            dust = None
            
            if self.state == 'jump_up' or self.state == 'jump_down' or self.state == ' wall_slide':
                if self.flip: 
                    dust = Particle(self.game,'dash_air',(self.rect().center[0] + 10,self.rect().center[1]),velocity=[1,0],frame=0)
                    self.velocity[0] = -5.0
                else: 
                    dust = Particle(self.game,'dash_air',(self.rect().center[0] - 10,self.rect().center[1]),velocity=[-1,0],frame=0)
                    self.velocity[0] = 5.0           
            else:
                if not self.flip:
                    dust = Particle(self.game,'dash_right',(self.rect().topleft[0]-1.4,self.rect().topleft[1]+2),velocity=[0,0],frame=0)
                    self.velocity[0] = 5.0
                else: 
                    #flip the dust particle effect
                    dust = Particle(self.game,'dash_left',(self.rect().topright[0]+1.4,self.rect().topright[1]+2),velocity=[0,0],frame=0)
                    self.velocity[0] = -5.0
            self.stamina -= 25

            self.game.particles.append(dust)
        
    def player_jump(self):
        
        if self.wall_slide: 
            self.jump_count = 1
            
            if self.collisions['left']:
                
                self.velocity[0] =  3.6
            if self.collisions['right']:
                
                self.velocity[0] = -3.6
            self.velocity[1] =-3.3
            air = Particle(self.game,'jump',(self.rect().centerx,self.rect().bottom), velocity=[0,0.1],frame=0)
            self.game.particles.append(air)

        if self.jump_count == 2:
            if self.state == 'jump_down':
                self.jump_count -=2
                self.velocity[1] = -3.5
                air = Particle(self.game,'jump',(self.rect().centerx,self.rect().bottom), velocity=[0,0.1],frame=0)
                self.game.particles.append(air)
            else: 
                self.jump_count -=1
                self.velocity[1] = -3.5    
            
        elif self.jump_count ==1: 
            self.jump_count -=1
            self.velocity[1] = -3.5  
            air = Particle(self.game,'jump',(self.rect().centerx,self.rect().bottom), velocity=[0,0.1],frame=0)
            self.game.particles.append(air)

    def equip_weapon(self,weapon):

        self.cur_weapon = weapon 
        self.equipped = True 
        self.cur_weapon.equip(self)

    def shoot_weapon(self,frame):
        #testing bullet firing
        if self.equipped: 
            if self.cur_weapon.rapid_firing:
                if frame % self.cur_weapon.fire_rate == 0:
                    test_shell_image = self.game.bullets['rifle_small'].copy()
                    test_shell = Bullet(self.game,self.cur_weapon.opening_pos,test_shell_image.get_size(),test_shell_image).copy()
                    self.cur_weapon.load(test_shell)

                    shot_bullet,smoke,angle = self.cur_weapon.shoot() 
                    self.game.Tilemap.bullets.append(shot_bullet)
                    self.game.bullets_on_screen.append(shot_bullet)
                    #rotate the images in the animation 
                    

            else: 
                test_shell_image = self.game.bullets['rifle_small'].copy()
                test_shell = Bullet(self.game,self.cur_weapon.opening_pos,test_shell_image.get_size(),test_shell_image).copy()
                self.cur_weapon.load(test_shell)

                shot_bullet,smoke,angle = self.cur_weapon.shoot() 

                self.game.Tilemap.bullets.append(shot_bullet)
                self.game.bullets_on_screen.append(shot_bullet)

            #add bullet drop particles and smoke particles 
                
            
            
                    
                    
    def toggle_rapid_fire(self):
        if self.equipped:
            self.cur_weapon.toggle_rapid_fire()


    def weapon_toggle_state(self):
        if self.equipped:
            return self.cur_weapon.rapid_firing 


class Bullet(PhysicsEntity): 
    def __init__(self,game,pos,size,sprite):
        super().__init__(game,'bullet',pos,size)
        self.damage = 1
        self.angle = 0
        self.speed = 0 
        self.sprite = sprite
        self.center = [self.sprite.get_width()/2,self.sprite.get_height()/2]
        self.set_state('in_place')
        self.frames_flown = 0
        self.test_tile = None
  
    def set_state(self, action):
        self.state = action

    def rect(self):
        
        return pygame.Rect(self.pos[0],self.pos[1],self.sprite.get_width(),self.sprite.get_height())

        

    def update_pos(self, tile_map,offset = (0,0)):
        self.collisions = {'up' :False,'down' : False, 'left': False, 'right': False }
        self.frames_flown +=1 
        
        if self.frames_flown >= 50:
            del self 
            return True
        
        #make collision detection more precise. 
        
        
        
        entity_rect = self.rect()
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                
                bullet_mask = pygame.mask.from_surface(self.sprite)
                tile_mask = pygame.mask.Mask((rect.width,rect.height))
                bullet_mask.fill()
                tile_mask.fill()
                offset = (entity_rect[0] - rect[0],entity_rect[1] - rect[1])
             
                if tile_mask.overlap(bullet_mask,offset):
                    collided_tile = tile_map.return_tile(rect)
                    if collided_tile.type == 'box':
                    #air = Particle(self.game,'jump',(self.rect().centerx,self.rect().bottom), velocity=[0,0.1],frame=0)
                        del tile_map.tilemap[str(collided_tile.pos[0]) + ';' + str(collided_tile.pos[1])]
                    
                    #destroy_box = Particle(self.game,'box_destroy',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                        destroy_box_smoke = Particle(self.game,'box_smoke',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                    #self.game.particles.append(destroy_box)
                        self.game.particles.append(destroy_box_smoke)
                        collided_tile.drop_item()
        
                    del self 
                    return True
        self.pos[0] += self.velocity[0] 

        
        
        
        entity_rect = self.rect()
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                #then you check for mask collision 
                
                bullet_mask = pygame.mask.from_surface(self.sprite)
                tile_mask = pygame.mask.Mask((rect.width,rect.height))
                bullet_mask.fill()
                tile_mask.fill()
                offset = (entity_rect[0] - rect[0],entity_rect[1] - rect[1]) 
             
                if tile_mask.overlap(bullet_mask,offset):
                    collided_tile = tile_map.return_tile(rect)
                    if collided_tile.type == 'box':
                    #air = Particle(self.game,'jump',(self.rect().centerx,self.rect().bottom), velocity=[0,0.1],frame=0)
                        del tile_map.tilemap[str(collided_tile.pos[0]) + ';' + str(collided_tile.pos[1])]
                    
                    #destroy_box = Particle(self.game,'box_destroy',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                        destroy_box_smoke = Particle(self.game,'box_smoke',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                    #self.game.particles.append(destroy_box)
                        self.game.particles.append(destroy_box_smoke)
                        collided_tile.drop_item()
        
                
                    del self 
                    return True
        self.pos[1] += self.velocity[1] 

        
        #collision with entities crude method....
            
        entity_rect = self.rect() 
        for enemy in self.game.enemies_on_screen:
            if entity_rect.colliderect(enemy.rect()):
                enemy.hit(self.damage)
                del self 
                return True 
            
        
             
    
    
    def render(self,surf,offset = (0,0)):
        #test_surface = pygame.Surface((self.sprite.get_width(),self.sprite.get_height()))
        #surf.blit(test_surface,(self.pos[0]-offset[0],self.pos[1]-offset[1]))
        surf.blit(self.sprite, (self.pos[0]-offset[0],self.pos[1]-offset[1]))
        

       

    def copy(self):
        return Bullet(self.game,self.pos,self.size,self.sprite)

