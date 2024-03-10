import pygame 
import random 
import math 
from scripts.particles import Particle,non_animated_particle


WEAPONS_THAT_CAN_RAPID_FIRE = {'rifle'}

class Weapon:
    def __init__(self,game,type,sprite,fire_rate,power,img_pivot):  
        self.game = game
        self.type = type 
        self.sprite = sprite 
        self.img_pivot = img_pivot
        self.flipped = False 
        self.rapid_firing = False 
        self.power=power
        self.knockback = [0,0]
        self.fire_rate = fire_rate
        self.magazine = []

        self.opening_pos = [0,0]
    
    def toggle_rapid_fire(self):
        if self.type in WEAPONS_THAT_CAN_RAPID_FIRE:
            self.rapid_firing = not self.rapid_firing

    
    def rotate(self,surface, angle, pivot, offset):
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  
        rotated_offset = offset.rotate(angle)  
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect  
    

    def equip(self,holder_entity):
        self.holder = holder_entity

    def load(self,bullet):
        self.magazine.append(bullet)

    def shoot(self,entity_vel):
        bullet = self.magazine.pop()
        if bullet: 
            #then you shoot the bullet.
            bullet.damage = self.power // 2 
            bullet.angle= self.angle_opening
            #rotate the bullet sprite around the center
            """
            bulletdisplay = pygame.Surface((bullet.sprite.get_width(),bullet.sprite.get_height()),pygame.SRCALPHA)
            bulletdisplay,bullet_rect = self.rotate(bulletdisplay,self.angle_opening,bullet.center,self.render_offset)
            """
            bullet.sprite = pygame.transform.rotate(bullet.sprite,bullet.angle)
            bullet.velocity = [math.cos(math.radians(-bullet.angle)) * self.power ,math.sin(math.radians(-bullet.angle))*self.power]  

            if bullet.velocity[0] > 0 :
                 
                bullet.pos = self.opening_pos.copy()
                bullet.pos[0] -= bullet.velocity[0]
                bullet.pos[1] += (0 if bullet.velocity[1] <0 else -bullet.velocity[1])
                bullet.flip = False 
            else: 
                bullet.pos = self.opening_pos.copy()
                if bullet.velocity[1] > 0 :
                    bullet.pos[1] -= bullet.velocity[1]
                bullet.flip = True 


            self.game.bullets_on_screen.append(bullet)
            self.knockback = [-bullet.velocity[0]/2,-bullet.velocity[1]/2]
            
            #append the shooting particles here instead of doing it in the entity class 
            shot_particle = Particle(self.game,'smoke'+'/'+self.type,self.opening_pos,velocity=[0,0],frame=0)
            rotated_shot_particle_images = [pygame.transform.rotate(image,bullet.angle) for image in shot_particle.animation.images]
            shot_particle.animation.images = rotated_shot_particle_images

            self.game.particles.append(shot_particle)
            #add non animated particles here to polish as well 
            for i in range(random.randint(6,13)):
                normal =[-bullet.velocity[1],bullet.velocity[0]] 
                factor = random.random()
                up_down = random.randint(-10,10)
                colors = [(253,245,216),(117,116,115),(30,30,30)]
                shot_muzzle_particle = non_animated_particle(self.opening_pos.copy(),random.choice(colors),[bullet.velocity[0]*20*factor + normal[0]* factor*up_down,bullet.velocity[1]*20*factor +normal[1]* factor*up_down],self.game.Tilemap,life = random.randint(1,5))
                self.game.non_animated_particles.append(shot_muzzle_particle)
            
            


        
    def copy(self):
        return Weapon(self.game,self.type,self.sprite,self.fire_rate,self.power,self.img_pivot)
        
    def update(self,cursor_pos):
        self.mpos = cursor_pos

    def render(self,surf,offset = (0,0)):
        #save surf to use when passing it to bullet 
        self.surf = surf 

        #you need to define the anchor point positions for every state of the player. 

        left_and_right_anchors = {  True: {"idle": {"left": (2,6), "right": (13,6)}, "walk": {"left": (2,6), "right": (13,6)},'run' :{"left": (1,6), "right": (8,5)} 
                                           ,'jump_up' :{"left": (0,4), "right": (9,4)},'jump_down' :{"left": (3,5), "right": (10,4)}
                                           ,'slide' :{ "left" : (11,9) ,"right": (11,9)} , 'wall_slide' : {"left": (4,5), "right": (8,5)} 
                                           },
                                    False: {"idle": {"left": (2,6), "right": (13,6)},"walk": {"left": (2,6), "right": (13,6)}, 'run' :{"left": (7,5), "right": (14,6)} 
                                           ,'jump_up' :{"left": (6,4), "right": (15,5)},'jump_down' :{"left": (2,4), "right": (7,5)}
                                           ,'slide' :{ "left": (4,9), "right": (4,9) }, 'wall_slide': {'left' : (7,5), 'right' : (11,5)} 
                                           },
        }

        #get the anchors. 

        self.left_anchor = left_and_right_anchors[self.holder.flip][self.holder.state]["left"]
        self.right_anchor = left_and_right_anchors[self.holder.flip][self.holder.state]["right"]
       
        rotate_cap_left = False
        rotate_cap_right = False

        
        if self.holder.state == 'slide' or self.holder.state == 'wall_slide':
            if self.holder.flip:
                rotate_cap_left = True 
            else: 
                rotate_cap_right = True 
        
        #get the angle, the pivot, and offset
        if self.flipped: 
            self.pivot = [self.holder.pos[0]+self.right_anchor[0]-offset[0]-1,self.holder.pos[1]+self.right_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(-self.sprite.get_rect().centerx + self.img_pivot[0],self.sprite.get_rect().centery - self.img_pivot[1] )       
        else: 
            self.pivot = [self.holder.pos[0]+self.left_anchor[0]-offset[0]+1,self.holder.pos[1]+self.left_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(self.sprite.get_rect().centerx - self.img_pivot[0], self.sprite.get_rect().centery - self.img_pivot[1])

        dx,dy = self.mpos[0] - self.pivot[0], self.mpos[1]- self.pivot[1]
        angle = math.degrees(math.atan2(-dy,dx)) 
        sprite_width = self.sprite.get_width()
        
        #separate angle varialble for the gun's opening - to apply angle cap and to pass onto firing bullet 
        self.angle_opening = angle 

        #flip transition lag exists. If it happens, don't blit the gun, and turn off the shooting function. 
        blitz = False

        #based on the angle, flip the sprite.If you are sliding, cap the angle. 
        if (angle > 90 and angle <= 180) or (angle < -90 and angle >= -180):
            if rotate_cap_right:
                if self.flipped:
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = False
                    blitz = True 
                if (angle > 90 and angle <= 180):
                    angle = -82
                elif (angle < -90 and angle >= -180):
                    angle = 83
                self.angle_opening = -angle 
            else: 
                if self.flipped != True: 
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = True 
                    blitz = True 
                angle += 180    
                angle = -angle
        else: 
            if rotate_cap_left:
                if self.flipped == False: 
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = True
                    blitz = True 
                if (angle >0 and angle <= 90) : 
                    angle = 65
                elif (angle <= 0 and angle >= -90):
                    angle =  -72
                self.angle_opening = 180-angle 
            else: 
                if self.flipped != False: 
                    self.sprite = self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = False  
                    blitz = True 
                angle = -angle


        weapon_display = pygame.Surface((self.sprite.get_width(),self.sprite.get_height()),pygame.SRCALPHA)
        weapon_display.blit(self.sprite,(0,0))
        rotated_image,rect = self.rotate(weapon_display,angle,self.pivot,self.render_offset)

        #the gun's opening position  
        #self.opening_pos[0] = self.pivot[0] + math.cos(math.radians(-self.angle_opening)) * sprite_width
        #self.opening_pos[1] = self.pivot[1] + math.sin(math.radians(-self.angle_opening)) * sprite_width
       
        self.opening_pos[0] = self.pivot[0] + offset[0]+ math.cos(math.radians(-self.angle_opening)) * sprite_width
        self.opening_pos[1] = self.pivot[1] + offset[1]+ math.sin(math.radians(-self.angle_opening)) * sprite_width

        if self.knockback[0] < 0: 
            self.knockback[0] = min(self.knockback[0] + 1.45, 0)
        if self.knockback[0] > 0 :
            self.knockback[0] = max(self.knockback[0] -1.45, 0)

        if self.knockback[1] < 0: 
            self.knockback[1] = min(self.knockback[1] + 1.45, 0)
        if self.knockback[1] > 0 :
            self.knockback[1] = max(self.knockback[1] -1.45, 0)

        #testSurf = pygame.Surface((2,2))

        if not blitz: 
            #surf.blit(testSurf,(self.opening_pos[0]-offset[0],self.opening_pos[1]-offset[1]))
            surf.blit(rotated_image,(rect.topleft[0] + self.knockback[0],rect.topleft[1] + self.knockback[1]))
         


class Wheelbot_weapon(Weapon):
    def __init__(self,game,animation):
        self.game = game 
        self.type = 'laser_weapon'
        self.animation = animation 
        self.img_pivot = [(2,8),(3,8)]
        self.flipped = False 
        self.rapid_firing = False 
        self.power = 12 
        self.knockback = [0,0]
        self.fire_rate = 0
        self.opening_pos = [0,0]
    
    def copy(self):
        return Wheelbot_weapon(self.game,self.animation.copy()) 
        
    def update(self,player_pos):
        self.animation.update()
        self.player_pos = player_pos

    def shoot(self):
        
        #you create a bullet 
        pass 

    def render(self,surf,offset = (0,0)):
        #save surf to use when passing it to bullet 
        self.surf = surf 

        img_pivot = self.img_pivot[0] if int(self.animation.frame / self.animation.img_dur) in [0,2] else self.img_pivot[1]

        #get the angle, the pivot, and offset
        if self.holder.flip: 
            self.sprite = pygame.transform.flip(self.animation.img(),True,False)
            self.right_anchor = (12,10)
            self.pivot = [self.holder.pos[0]+self.right_anchor[0]-offset[0],self.holder.pos[1]+self.right_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(-self.sprite.get_rect().centerx + img_pivot[0],self.sprite.get_rect().centery - img_pivot[1] )       
        else: 
            self.sprite = self.animation.img()
            self.left_anchor = (8,10)
            self.pivot = [self.holder.pos[0]+self.left_anchor[0]-offset[0],self.holder.pos[1]+self.left_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(self.sprite.get_rect().centerx - img_pivot[0], self.sprite.get_rect().centery - img_pivot[1])

        """
        mpos = pygame.mouse.get_pos()
        mpos = ((mpos[0]/2),(mpos[1]/2))

        dx,dy = mpos[0] - self.pivot[0], mpos[1]- self.pivot[1]
        """
        
        self.player_pos = (self.player_pos[0]-offset[0]+8,self.player_pos[1]-offset[1]+8)
        dx,dy = self.player_pos[0] - self.pivot[0], self.player_pos[1]- self.pivot[1]
       
        if self.holder.flip: 
            dx = -dx
        else:
            dy = -dy

        
        angle = math.degrees(math.atan2(-dy,dx)) 
       

        sprite_width = self.sprite.get_width()

        

        
        #separate angle varialble for the gun's opening - to apply angle cap and to pass onto firing bullet 
        self.angle_opening = angle 

        #flip transition lag exists. If it happens, don't blit the gun, and turn off the shooting function. 
        blitz = False
        """
        #based on the angle, flip the sprite.If you are sliding, cap the angle. 
        if (angle > 90 and angle <= 180) or (angle < -90 and angle >= -180):
            if rotate_cap_right:
                if self.flipped:
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = False
                    blitz = True 
                if (angle > 90 and angle <= 180):
                    angle = -82
                elif (angle < -90 and angle >= -180):
                    angle = 83
                self.angle_opening = -angle 
            else: 
                if self.flipped != True: 
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = True 
                    blitz = True 
                angle += 180    
                angle = -angle
        else: 
            if rotate_cap_left:
                if self.flipped == False: 
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = True
                    blitz = True 
                if (angle >0 and angle <= 90) : 
                    angle = 65
                elif (angle <= 0 and angle >= -90):
                    angle =  -72
                self.angle_opening = 180-angle 
            else: 
                if self.flipped != False: 
                    self.sprite = self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = False  
                    blitz = True 
                angle = -angle
        """

        weapon_display = pygame.Surface((self.sprite.get_width(),self.sprite.get_height()),pygame.SRCALPHA)
        weapon_display.blit(self.sprite,(0,0))
        rotated_image,rect = self.rotate(weapon_display,angle,self.pivot,self.render_offset)

        #the gun's opening position  
        #self.opening_pos[0] = self.pivot[0] + math.cos(math.radians(-self.angle_opening)) * sprite_width
        #self.opening_pos[1] = self.pivot[1] + math.sin(math.radians(-self.angle_opening)) * sprite_width

       

        self.opening_pos[0] = self.pivot[0] + offset[0]+ math.cos(math.radians(self.angle_opening +180 if self.holder.flip else self.angle_opening)) * sprite_width
        self.opening_pos[1] = self.pivot[1]-3 + offset[1]+ math.sin(math.radians(-self.angle_opening if self.holder.flip else self.angle_opening)) * sprite_width
        
        if self.knockback[0] < 0: 
            self.knockback[0] = min(self.knockback[0] + 1.45, 0)
        if self.knockback[0] > 0 :
            self.knockback[0] = max(self.knockback[0] -1.45, 0)

        if self.knockback[1] < 0: 
            self.knockback[1] = min(self.knockback[1] + 1.45, 0)
        if self.knockback[1] > 0 :
            self.knockback[1] = max(self.knockback[1] -1.45, 0)
        
        #testSurf = pygame.Surface((2,2))

        if not blitz: 
            #surf.blit(testSurf,(self.opening_pos[0]-offset[0],self.opening_pos[1]-offset[1]))
            outline = pygame.mask.from_surface(rotated_image)
            for offset_ in [(-1,0),(1,0),(0,-1),(0,1)]:
                surf.blit(outline.to_surface(unsetcolor=(255,255,255,0),setcolor=(0,0,0,255)),(rect.topleft[0] +offset_[0],rect.topleft[1]+offset_[1]))
            surf.blit(rotated_image,(rect.topleft[0] + self.knockback[0],rect.topleft[1] + self.knockback[1]))















        """
        #save surf to use when passing it to bullet 
        self.surf = surf 

        #you need to define the anchor point positions for every state of the player. 
 

        
        
       
        
        rotate_cap_left = False
        rotate_cap_right = False

        
        if self.holder.state == 'slide' or self.holder.state == 'wall_slide':
            if self.holder.flip:
                rotate_cap_left = True 
            else: 
                rotate_cap_right = True 
        
        
        #get the angle, the pivot, and offset
        img_pivot = self.img_pivot[0] if int(self.animation.frame / self.animation.img_dur) in [0,2] else self.img_pivot[1]
        
        if self.holder.flip: 
      
            self.sprite = pygame.transform.flip(self.animation.img(),True,False)
            self.right_anchor = (12,9)
            self.pivot = [self.holder.pos[0]+self.right_anchor[0]-offset[0]-1,self.holder.pos[1]+self.right_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(-self.animation.img().get_rect().centerx + img_pivot[0],self.animation.img().get_rect().centery - img_pivot[1] )       
        else:
            self.sprite = self.animation.img()
            self.left_anchor = (6,10)
            self.pivot = [self.holder.pos[0]+self.left_anchor[0]-offset[0]+1,self.holder.pos[1]+self.left_anchor[1] -offset[1]]
            self.render_offset = pygame.math.Vector2(self.animation.img().get_rect().centerx - img_pivot[0], self.animation.img().get_rect().centery - img_pivot[1])

        dx,dy = self.player_pos[0] - self.pivot[0], self.player_pos[1]- self.pivot[1]
        angle = math.degrees(math.atan2(-dy,dx)) 
       
        b = 90 - math.acos(3/math.hypot(self.player_pos[0] - self.pivot[0], self.player_pos[1] - self.pivot[1]))

        angle = angle - b 

        
        sprite_width = self.animation.img().get_width()

        
        
        #separate angle varialble for the gun's opening - to apply angle cap and to pass onto firing bullet 
        self.angle_opening = angle 

        #flip transition lag exists. If it happens, don't blit the gun, and turn off the shooting function. 
        blitz = False

        #based on the angle, flip the sprite.If you are sliding, cap the angle. 
        
        if (angle > 90 and angle <= 180) or (angle < -90 and angle >= -180):
            
            if rotate_cap_right:
                if self.flipped:
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = False
                    blitz = True 
                if (angle > 90 and angle <= 180):
                    angle = -82
                elif (angle < -90 and angle >= -180):
                    angle = 83
                self.angle_opening = -angle 
            else: 
            
            if self.flipped != True: 
                self.sprite = pygame.transform.flip(self.animation.img(),True,False)
                self.flipped = True 
                blitz = True 
            angle += 180    
            angle = -angle
        else:
             
            if rotate_cap_left:
                if self.flipped == False: 
                    self.sprite = pygame.transform.flip(self.sprite,True,False)
                    self.flipped = True
                    blitz = True 
                if (angle >0 and angle <= 90) : 
                    angle = 65
                elif (angle <= 0 and angle >= -90):
                    angle =  -72
                self.angle_opening = 180-angle 
            else: 
            
            if self.flipped != False: 
                self.sprite = pygame.transform.flip(self.animation.img(),True,False)
                self.flipped = False  
                blitz = True 
            angle = -angle
        

        weapon_display = pygame.Surface((self.sprite.get_width(),self.sprite.get_height()),pygame.SRCALPHA)
        weapon_display.blit(self.sprite,(0,0))

        
            
        rotated_image,rect = self.rotate(weapon_display,angle,self.pivot,self.render_offset)

        #the gun's opening position  
        #self.opening_pos[0] = self.pivot[0] + math.cos(math.radians(-self.angle_opening)) * sprite_width
        #self.opening_pos[1] = self.pivot[1] + math.sin(math.radians(-self.angle_opening)) * sprite_width
       
        
        self.opening_pos[0] = self.pivot[0] + offset[0]+ math.cos(math.radians(-self.angle_opening)) * sprite_width
        self.opening_pos[1] = self.pivot[1] + offset[1]+ math.sin(math.radians(-self.angle_opening)) * sprite_width
       
        
        if self.knockback[0] < 0: 
            self.knockback[0] = min(self.knockback[0] + 1.45, 0)
        if self.knockback[0] > 0 :
            self.knockback[0] = max(self.knockback[0] -1.45, 0)

        if self.knockback[1] < 0: 
            self.knockback[1] = min(self.knockback[1] + 1.45, 0)
        if self.knockback[1] > 0 :
            self.knockback[1] = max(self.knockback[1] -1.45, 0)
        

        print(angle)
        testSurf = pygame.Surface((2,2))

        if not blitz: 
            surf.blit(testSurf,(self.opening_pos[0]-offset[0],self.opening_pos[1]-offset[1]))
           
            surf.blit(rotated_image,(rect.topleft[0] ,rect.topleft[1] ))
            #surf.blit(testSurf,(rect.topleft[0] ,rect.topleft[1] ))
         

        """