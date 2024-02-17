import pygame

class Bar():
    def __init__(self,x,y,w,h,max_resource):
        self.x = x
        self.y = y
        self.w = w
        self.h = h 
        self.cur_resource = max_resource
        self.max_resource = max_resource
    
    def update_render_pos(self,x,y):
        self.x = x
        self.y = y

    def render(self,surf,offset = (0,0)):
        #calculate health ratio 
        ratio = self.hp/ self.max_hp
        pygame.draw.rect(surf,"black",(self.x-offset[0],self.y-offset[1],self.w,self.h))
        pygame.draw.rect(surf,"red",(self.x-offset[0],self.y-offset[1],self.w*ratio,self.h))

class HealthBar(Bar):
    def __init__(self,x,y,w,h,max_hp):
        super().__init__(x,y,w,h,max_hp)

    def render(self,surf,offset = (0,0)):
        #calculate health ratio 
        ratio = self.cur_resource/ self.max_resource
        pygame.draw.rect(surf,(0,0,0,0),(self.x-offset[0],self.y-offset[1],self.w,self.h))
        pygame.draw.rect(surf,(139,0,20,255),(self.x-offset[0],self.y-offset[1],self.w*ratio,self.h))
        

class StaminaBar(Bar):
    def __init__(self,x,y,w,h,max_stamina):
        super().__init__(x,y,w,h,max_stamina)

    def render(self,surf,offset = (0,0)):
        #calculate health ratio 
        ratio = self.cur_resource/ self.max_resource
        pygame.draw.rect(surf,(0,0,0,0),(self.x-offset[0],self.y-offset[1],self.w,self.h))
        pygame.draw.rect(surf,(61,44,116,255),(self.x-offset[0],self.y-offset[1],self.w*ratio,self.h))