import pygame 

class Background:
    def __init__(self,game,picture,depth):
        self.game = game 
        self.picture = picture 
        self.depth = depth 
        self.surf = pygame.Surface((self.picture.get_width(),self.picture.get_height()))

    def render(self,surf,offset= (0,0)): 
        pass     
    
