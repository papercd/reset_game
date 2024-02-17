import os 
import pygame 


#so in here we are going to define a function that creates pygame image objects
#and returns them, so that we can simplify our code when creating our assets 
#dictionary.The assets dictionary is going to contain lists as well, lists of sprite objects
#for our grass, stone, and clouds, etc.

BASE_PATH = 'data/images/'

def load_image(path,background = 'black'):
     
    
    if background == 'black':
        sprite = pygame.image.load(BASE_PATH + path).convert()
        sprite.set_colorkey((0,0,0))
    elif background == 'transparent': 
        sprite= pygame.image.load(BASE_PATH + path)
    return sprite 


#now the this load_images function will get all the sprites within one directory and turn them into a list.

def load_images(path,background = 'black'):
    sprites = []
    #the sorted() method will turn the list into an alphabetically-sorted list.
    for sprite_name in sorted(os.listdir(BASE_PATH + path)):
        sprites.append(load_image(path+ '/' + sprite_name,background))

    return sprites




class Animation: 
    def __init__(self, images, img_dur = 5, halt = False, loop = True):
        self.images = images 
        self.loop = loop 
        self.halt = halt
        self.img_dur = img_dur 
        self.done = False 
        self.frame = 0

    def copy(self):
        return Animation(self.images,self.img_dur,self.halt,self.loop)
    
    def update(self):
        if self.halt: 
             self.frame = min(self.frame+1,self.img_dur * len(self.images) -1)
        else: 
            if self.loop:
                self.frame = (self.frame+1) % (self.img_dur * len(self.images))
            else: 
                self.frame = min(self.frame+1,self.img_dur * len(self.images) -1)
                if self.frame >= self.img_dur *len(self.images) -1:
                    self.done = True 


    def img(self):
        return self.images[int(self.frame / self.img_dur)]