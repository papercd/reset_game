import pygame
import random 

class Particle: 
    def __init__(self,game, p_type, pos, velocity = [0,0], frame = 0):
        self.game = game 
        self.type = p_type
        self.pos = list(pos)
        self.velocity = velocity
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame
        

  
            

    def update(self):
        kill = False 
        if self.animation.done: 
            kill = True 
        
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill 
    
    def render(self,surf, offset= (0,0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0]-offset[0]-img.get_width()//2,self.pos[1]- offset[1]-img.get_height()//2))



class non_animated_particle():
    def __init__(self,pos,color,velocity,tilemap,life = 60):
        self.time = 0
        self.pos = pos
        self.color = color
        self.tilemap = tilemap
        self.velocity = velocity
        self.life = life 
        self.create_surf()
    
    #the default non-animated particle is a circle. 
    def create_surf(self):
        self.image = pygame.Surface((1,1)).convert_alpha()
        self.image.set_colorkey("black")
        pygame.draw.rect(self.image,self.color, pygame.Rect(0,0,1,1))
        self.rect  = self.image.get_rect()
    
   
    def update(self,dt):
        self.time +=1
        for rect in self.tilemap.physics_rects_around(self.pos,(1,1)):
            if self.rect.colliderect(rect):
                return True 
        if self.time > self.life:
            return True 
       
        self.pos[0] += self.velocity[0] * dt 
        self.pos[1] += self.velocity[1] * dt 
        self.rect.topleft = self.pos 
        return False 
    
    def render(self,surf,offset = (0,0)):
        surf.blit(self.image,(self.pos[0]- offset[0],self.pos[1]-offset[1]))



class bullet_collide_particle(non_animated_particle):
    def __init__(self,groups,pos,color,direction,speed):
        super().__init__(groups,pos,color,direction,speed)

    
    def create_surf(self):
        pass 