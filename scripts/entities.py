#alright, so this is where I am going to implement physics for the objects 
#of my game. 
import random
import pygame 
from scripts.particles import Particle
from scripts.health import HealthBar,StaminaBar

class PhysicsEntity:
    #alright, what does a physics entity need? it needs a size, in 2 dimensions, 
    #and for my game, a physics entity will need a sprite, a position, and velocity. We would also need to define
    #the type of entity it is. Because there are different objects we can render in the game. Like rocks, grass, players. etc.
    #I will also add the game as a parameter so that any physics entity can access any other entity in the game. 

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
        #ok, so this function allows us to update the position of the physics entity
        #when updating the position of the physics entity, we need to think about movement in two dimensions. 
        #the x-dimension, where the movement is directly modified by the player, and the y-dimension, where gravity 
        #is the only factor affecting its movement. 

        #I am going to add the gravity factor here now.gravity affects the player to accelerate downwards. meaning that velocity increases every frame, until the 
        #velocity reaches terminal velocity. 


        #this velocity part should be unique to the player, but whatever. I can change this later. 
        self.velocity[1] = min(5,self.velocity[1] +0.2)

        if self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0]+0.25, 0)  
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] -0.25,0)

         

        #I will define a frame movement variable that defines how much movement there should be in this particular frame.
        if self.cut_movement_input:
            frame_movement = (self.velocity[0],self.velocity[1])
        else: 
            frame_movement =  (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        #and this works because think of it like a frame being a single point in time. the current position in that frame 
        #plus the velocity of the entity in that frame would give you? The position of the entity in the next frame.            

        #add the collision detection here. So, a physics entity has a size. which represents the dimensions of the encompassing rectangle
        #if any of the edges of the rectangle meets with an edge of any other rectangle, the position is set to the edge of the
        # rectangle that is being collided against. 
        
    
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



    #for any render function, you will need to pass it the surface on which you want to blit the object on. 
    def render(self,surf,offset):
        #now here you need a sprite, and you need the position on which you want to print this on. 
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
        super().__init__(game,pos,size,'Canine')
        
    def collision_rect(self):
        return pygame.Rect(self.pos[0]+3,self.pos[1]+4,self.size[0]-6,self.size[1]-8)


    def set_state(self,action):
        if action != self.state: 
            self.state = action 
            self.animation = self.game.enemies[self.type + '/' + self.color  + '/'+ self.state].copy() 

    def update(self,tilemap,movement = (0,0)):
        #now I want to make the AI of the enemies a bit better 

        self.air_time +=1
        if self.collisions['down']:
            self.air_time = 0

        if self.state == 'hit':
            if self.animation.done == True: 
                self.set_state('idle')
        else: 
            if self.walking :
                #things to check when you are walking 

                """
                if movement[0] != 0:
                    self.set_state('run')

                if tilemap.solid_check((self.rect().centerx + (-21 if self.flip else 21),self.pos[1]+27)):
                    
                    
                    if tilemap.solid_check((self.rect().centerx + (-21 if self.flip else 21),self.rect().centery)):
                        if tilemap.solid_check(((self.rect().centerx + (-21 if self.flip else 21),self.pos[1] - 8))):
                            self.flip = not self.flip 
                        else: 
                            self.velocity[1] = -3
                            self.velocity[0] = (-0.5 if self.flip else 0.5)
                            self.set_state('jump_up')
                    else: 
                        movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                else: 
                    if tilemap.solid_check((self.rect().centerx + (-37 if self.flip else 37),self.rect().centery+59)):
                        movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
                    else: 
                        if self.air_time > 3:
                            self.set_state('jump_up')
                            
                        else: 
                            self.flip = not self.flip 
                    
                self.walking = max(0,self.walking - 1)
                """
            elif random.random() < 0.01:
                #things to do when you aren't walking 
                self.walking = random.randint(30,120)
        super().update_pos(tilemap,movement=movement)
        
        
        #you need to implement a new collision detection for sprites that are bigger than a single tile 
        

#I realized that to specifically add a sprite to the player, I would need to create a separate class that is 
#inherited from the PhysicsEntity class.
        
class PlayerEntity(PhysicsEntity):
    def __init__(self,game,pos,size):
        #attributes required to implement weapon equipment 
        self.equipped = False 
        self.cur_weapon = None 

    

        super().__init__(game,'player',pos,size)

        self.stamina = 100
        self.health = 200

        self.health_bar = HealthBar(32,300,200,4,self.health)
        self.stamina_bar =  StaminaBar(32,310,200,4,self.stamina)

        self.health_UI = self.game.assets['health_stamina_UI']
        self.stamina_UI = self.game.assets['health_stamina_UI']

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
            #wait until stamina is above 60 and you aren't fatigued anymore. 
            
            new_movement[0] = new_movement[0] *1.5/1.6
            if self.stamina >= 60:
                self.fatigued = False 
        else:
            #if you aren't fatigued, then you can run. 
            if self.stamina > 10: 
                #then you allow speedup. 
                if self.running: 
                    if new_movement[0] != 0:
                        self.stamina = max(0,self.stamina-1.3)
            else: 
                #you are fatigued. you can't run. 
                self.fatigued = True 
                if self.running: 
                    new_movement[0] = new_movement[0] *1.5/1.6
             


        """
        if self.stamina > 10 and not self.fatigued:
            #then you allow speedup. 
            if self.running: 
                if movement[0] != 0:
                    self.stamina =max(0,self.stamina-1.3) 
        else: 
            #you don't speed up. 
            if self.running: 
                new_movement[0] = new_movement[0]*1.5 / 1.6
        """

        super().update_pos(tile_map, new_movement)


        #every frame, the stamina is increased by 0.7
        

        self.stamina = min(100, self.stamina + 0.7)
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
                
                self.set_state('run')
                 
                
 
                #self.frame_between_taps = self.frame_count
                #self.frame_count_between_taps = min(1000,self.frame_count_between_taps)
               
                """
                elif (self.frame_count_between_taps > 1 and self.frame_count_between_taps <20) :
                
                    if self.boost_on_next_tap and self.running_time < 10:
                        if self.stamina >=40:
                            #then you boost.
                            dust = None
                            
                            if movement[0] > 0 and self.boost_dir == False:
                                dust = Particle(self.game,'dash_right',(self.rect().topleft[0]-1.4,self.rect().topleft[1]+2),velocity=[0,0],frame=0)
                                self.velocity[0] = 5.0
                            if movement[0] < 0 and self.boost_dir:
                                
                                #flip the dust particle effect
                                dust = Particle(self.game,'dash_left',(self.rect().topright[0]+1.4,self.rect().topright[1]+2),velocity=[0,0],frame=0)
                                self.velocity[0] = -5.0

                            
                            self.game.particles.append(dust)
                            self.boost_on_next_tap = False

                            #if you dash, decrement the stamina by 40
                            self.stamina -= 40
                    else:
                        if movement[0] > 0:
                            self.boost_dir = False
                        if movement[0] < 0: 
                            self.boost_dir = True 
                        self.boost_on_next_tap = True 
                    self.running_time = 0
                else: 
                    self.boost_on_next_tap = False 
                    self.running_time = 0

                self.frame_count_between_taps =0
                """
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


        
    
    def render(self,surf,offset):
        super().render(surf,offset)

        #render the health bar and the stamina bar
        surf.blit(self.health_UI,(self.health_bar.x-2,self.health_bar.y-2)) 
        self.health_bar.render(surf,(0,0))

        surf.blit(self.stamina_UI,(self.stamina_bar.x-2,self.stamina_bar.y-2)) 
        self.stamina_bar.render(surf,(0,0))

        if self.equipped: 
            self.cur_weapon.render(surf,offset)
    
    def dash(self):
        dust = None
             
        if not self.flip:
            dust = Particle(self.game,'dash_right',(self.rect().topleft[0]-1.4,self.rect().topleft[1]+2),velocity=[0,0],frame=0)
            self.velocity[0] = 5.0
        else: 
            #flip the dust particle effect
            dust = Particle(self.game,'dash_left',(self.rect().topright[0]+1.4,self.rect().topright[1]+2),velocity=[0,0],frame=0)
            self.velocity[0] = -5.0

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
        #return pygame.Rect(self.pos[0]+self.sprite.get_width()/2,self.pos[1]+self.sprite.get_height()/2,1,1)
        return pygame.Rect(self.pos[0],self.pos[1],self.sprite.get_width(),self.sprite.get_height())

        

    def update_pos(self, tile_map,offset = (0,0)):
        self.collisions = {'up' :False,'down' : False, 'left': False, 'right': False }
        self.frames_flown +=1 
        
        if self.frames_flown >= 50:
            del self 
            return True
        
        #make collision detection more precise. 
        
        self.pos[0] += self.velocity[0] 
        
        entity_rect = self.rect()
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                
                
                
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
        
        entity_rect = self.rect()
        for rect in tile_map.physics_rects_around(self.pos,self.size):
            if entity_rect.colliderect(rect):
                #then you check for mask collision 
                
                
                collided_tile = tile_map.return_tile(rect)
                if collided_tile.type == 'box':
                    del tile_map.tilemap[str(collided_tile.pos[0]) + ';' + str(collided_tile.pos[1])]
                    
                    #destroy_box = Particle(self.game,'box_destroy',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                    destroy_box_smoke = Particle(self.game,'box_smoke',(rect.centerx,rect.centery),velocity=[0,0],frame = 10)  
                    #self.game.particles.append(destroy_box)
                    self.game.particles.append(destroy_box_smoke)
                    collided_tile.drop_item()
                    
                
                del self 
                return True
        

        
        #collision with entities crude method....
            
        entity_rect = self.rect() 
        for enemy in self.game.enemies_on_screen:
            if entity_rect.colliderect(enemy.rect()):
                
                enemy.set_state('hit')
                enemy.animation.frame =0
                del self 
                return True 
        
             
    
    
    def render(self,surf,offset = (0,0)):
        test_surface = pygame.Surface((self.sprite.get_width(),self.sprite.get_height()))
        #surf.blit(test_surface,(self.pos[0]-offset[0],self.pos[1]-offset[1]))
        surf.blit(self.sprite, (self.pos[0]-offset[0],self.pos[1]-offset[1]))
        

       

    def copy(self):
        return Bullet(self.game,self.pos,self.size,self.sprite)


class Box(PhysicsEntity):
    def __init__(self,game,pos):
        super().__init__(game,'box',pos,(12,12))

    def set_state(self,action):
        self.state = action

    def update_pos(self, tile_map, movement=(0, 0)):
        #it doesn't move right now, I will add this later. 
        self.collisions = {'up' :False,'down' : False, 'left': False, 'right': False }

        self.entity_rect= self.rect() 
        return False 

    def render(self,surf,offset): 
        test_surface = pygame.Surface((12,12))
        surf.blit(test_surface,(self.pos[0] - offset[0],self.pos[1]- offset[1]))

        #check for collision with a bullet. 

