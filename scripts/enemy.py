import pygame 
from particles import Particle 

from entities import PhysicsEntity


class Enemy(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'enemy',pos,size)



    