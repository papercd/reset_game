
import pygame
import random
import math
import sys 
from scripts.tilemap import Tilemap
from scripts.utils import load_image,load_images,Animation
from scripts.entities import PlayerEntity,Canine
from scripts.clouds import Clouds
from scripts.particles import Particle
from scripts.cursor import Cursor
from scripts.weapons import Weapon 



class myGame:
    def __init__(self):
        pygame.init() 
        pygame.display.set_caption('myGame')
        self.screen = pygame.display.set_mode((1040,652))
        self.clock = pygame.Clock()
        self.display = pygame.Surface((self.screen.get_width()//2,self.screen.get_height()//2),pygame.SRCALPHA)
        self.display_2 = pygame.Surface((self.screen.get_width()//2,self.screen.get_height()//2))

        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'box' : load_images('tiles/box'),

            'player' : load_image('entities/player.png'),
            'background': load_image('background.png'),
            'test_background' : load_image('test_background.png'),

            'cursor/default' : load_image('cursor/default_cursor.png',background='black'),
            'crosshair' : load_image('cursor/crosshair.png'),


            'clouds': load_images('clouds/default'),
            'gray1_clouds' : load_images('clouds/gray1',background = 'transparent'),
            'gray2_clouds' : load_images('clouds/gray2',background = 'transparent'),
            
            'player/holding_gun/idle' : Animation(load_images('entities/player/holding_gun/idle',background='transparent'), img_dur =6),
            'player/holding_gun/run' : Animation(load_images('entities/player/holding_gun/run',background='transparent'), img_dur =4),

            'player/holding_gun/jump_up' : Animation(load_images('entities/player/holding_gun/jump/up',background='transparent'), img_dur =5),
            'player/holding_gun/jump_down' : Animation(load_images('entities/player/holding_gun/jump/down',background='transparent'), img_dur =5,halt=True),
           

            'player/holding_gun/slide' : Animation(load_images('entities/player/slide',background='transparent'), img_dur =5),
            'player/holding_gun/wall_slide' : Animation(load_images('entities/player/wall_slide',background='transparent'), img_dur =4),
            'player/holding_gun/walk' : Animation(load_images('entities/player/holding_gun/walk',background='transparent'), img_dur =9),


            'health_UI' : load_image('ui/health/0.png',background='transparent'),
            'stamina_UI' : load_image('ui/stamina/0.png',background='transparent'),


            'player/idle' : Animation(load_images('entities/player/idle',background='transparent'), img_dur =6),
            'player/run' : Animation(load_images('entities/player/run',background='transparent'), img_dur =4),

            'player/jump_up' : Animation(load_images('entities/player/jump/up',background='transparent'), img_dur =5),
            'player/jump_down' : Animation(load_images('entities/player/jump/down',background='transparent'), img_dur =5,halt=True),
           

            'player/slide' : Animation(load_images('entities/player/slide',background='transparent'), img_dur =5,halt = True),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide',background='transparent'), img_dur =4),
            

            'particle/box_destroy' : Animation(load_images('particles/box',background='transparent'),img_dur= 3,loop= False),
            'particle/box_smoke' : Animation(load_images('particles/box_break',background='black'),img_dur= 3,loop= False),
            
            'particle/leaf':Animation(load_images('particles/leaf'),img_dur =20,loop=False),
            'particle/jump':Animation(load_images('particles/jump',background= 'black'),img_dur= 2, loop= False),
            'particle/dash_left' : Animation(load_images('particles/dash/left',background='black'),img_dur=1,loop =False),
            'particle/dash_right' : Animation(load_images('particles/dash/right',background='black'),img_dur=1,loop =False),
            'particle/dash_air' : Animation(load_images('particles/dash/air',background='black'),img_dur=2,loop =False),
            

            'particle/rifle' : Animation(load_images('particles/rifle',background='black'),img_dur=2,loop=False),

            #'particle/rifle_small' : Animation(load_images('particles/bullet_collide_smoke/rifle/small',background='black'),img_dur=2,loop=False),

        } 

        self.enemies = {
            'Canine/black/idle' : Animation(load_images('entities/enemy/Canine/black/idle',background='transparent'),img_dur= 8),
            'Canine/black/run' : Animation(load_images('entities/enemy/Canine/black/run',background= 'transparent'),img_dur= 6),
            'Canine/black/jump_up': Animation(load_images('entities/enemy/Canine/black/jump/up',background= 'transparent'),img_dur= 1,loop = False),
            'Canine/black/jump_down': Animation(load_images('entities/enemy/Canine/black/jump/down',background= 'transparent'),img_dur= 2,loop = False),
            'Canine/black/hit': Animation(load_images('entities/enemy/Canine/black/hit',background= 'transparent'),img_dur= 5,loop=False),
            'Canine/black/grounded_death': Animation(load_images('entities/enemy/Canine/black/death/grounded',background= 'transparent'),img_dur= 5,loop=False),
        }


        self.weapons = {
            'ak' : Weapon(self,'rifle',load_image('weapons/ak_holding.png',background='transparent'), 5,15,(2,2))
        }

        
        self.bullets = {
            'rifle_small' : load_image('bullets/rifle/small.png',background='transparent'),
        }
        self.bullets_on_screen = []
        

        self.gray_clouds = Clouds(self.assets['gray1_clouds'],count = 8,direction='right')
        self.opp_gray_clouds = Clouds(self.assets['gray2_clouds'],count = 6, direction= 'left')

        self.Tilemap = Tilemap(self,tile_size=16)
        self.Tilemap.load('map.json')

        #adding leaf shedding particle effects by locating where the trees are in the tilemap and spawning leaves in a certain location with regards to 
        #that tree location. 
       
    
        self.leaf_spawners = []
        for tree in self.Tilemap.extract([('large_decor',2)],keep = True):
            self.leaf_spawners.append(pygame.Rect(4+tree.pos[0], 4+tree.pos[1],23,13))
        

        self.particles = []
        self.non_animated_particles = []

        self.PLAYER_DEFAULT_SPEED = 1.8
        self.player = PlayerEntity(self,(50,50),(16,16))
        self.player_movement = [False,False]
        self.scroll = [0,0]

        #dash variables
        self.boost_ready = False 
        self.timer = 0
        self.time_increment = False
        
        #cursor object 
        pygame.mouse.set_visible(True)
        self.cursor = Cursor(self,(50,50),(4,4),'default')

        #weapon equip
        self.player.equip_weapon(self.weapons['ak'])
        self.frame_count = 0
        self.reset = True 

        
        self.enemies_on_screen = []

        for spawner in self.Tilemap.extract([('spawners',0),('spawners',1)]):   
            if spawner.variant == 0:
                self.player.pos = spawner.pos
            else: 

                #changed later 
                self.enemies_on_screen.append(Canine(self,spawner.pos,(34,23),'black'))
       

    def run(self):
        while True: 
            
            self.timer += self.time_increment
            if self.timer > 20:
                self.boost_ready = False 
                self.time_increment = False 
                self.timer = 0


            self.frame_count = (self.frame_count+1) % 60 
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() /2 - self.scroll[0])/30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() /2 - self.scroll[1])/30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:
                if random.random() * 399999 < rect.width * rect.height: 
                    pos = (rect.x +random.random()* rect.width,rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self,'leaf',pos,velocity=[random.randrange(-100,100)/1000,0.3], frame = random.randint(0,20)))

           
            self.display.fill((0,0,0,0))

            #you should now add a cap to how much the map can move in either dimension, which you are going to add later. 
            background = pygame.transform.scale(self.assets['test_background'],(self.display.get_width()*1.4,self.display.get_height()*1.4))
            self.display_2.blit(background, [0-(0.4*self.display.get_width())/2- (render_scroll[0]/350) ,0-(0.4*self.display.get_height())/2 - (render_scroll[1]/350)])

            self.gray_clouds.update()
            self.gray_clouds.render(self.display_2,render_scroll)

            self.opp_gray_clouds.update()
            self.opp_gray_clouds.render(self.display_2,render_scroll)


            #We don't need the code here. 
            self.Tilemap.render(self.display,render_scroll)

            for enemy in self.enemies_on_screen.copy():
                kill = enemy.update(self.Tilemap,self.player.pos,(0,0))
                enemy.render(self.display_2,offset = render_scroll)
                if kill:
                    self.enemies_on_screen.remove(enemy)

        

            #running check
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT]:
                self.player.running = True 
            else: 
                self.player.running = False
            

           
            
            #rapid fire and single fire toggle 
            if pygame.mouse.get_pressed()[0]:
                if self.player.weapon_toggle_state():
                    #then you shoot. 
                    self.player.shoot_weapon(self.frame_count)
                else:
                    #you shoot, once. 
                    if self.reset == True: 
                        self.player.shoot_weapon(self.frame_count)
                        self.reset = False 
            elif pygame.mouse.get_pressed()[0] == False:
                self.reset = True 
             

            #code for the cursor 
            self.cursor.update()
            self.cursor.render(self.display)
            
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,180),unsetcolor=(0,0,0,0))

            for offset in [(-1,0),(1,0),(0,-1),(0,1)]:
                self.display_2.blit(display_sillhouette,offset)
           

            for particle in self.particles.copy():
                if particle == None: 
                    self.particles.remove(particle)
                else:
                    kill =particle.update()
                    particle.render(self.display,offset = render_scroll)
                    if particle.type =='leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill: 
                        self.particles.remove(particle)

            for particle in self.non_animated_particles.copy():
                pass 


            for bullet in self.bullets_on_screen:
                if bullet == None: 
                    self.bullets_on_screen.remove(bullet)
                else: 
                    kill = bullet.update_pos(self.Tilemap)
                    bullet.render(self.display,offset = render_scroll)
                
                    if kill: 
                        self.bullets_on_screen.remove(bullet)


            
                        
            for event in pygame.event.get():
                #We need to define when the close button is pressed on the window. 
                        
                if event.type == pygame.QUIT: 
                    #then pygame is closed, and the system is closed. 
                    pygame.quit() 
                    sys.exit() 
                
                #define when the right or left arrow keys are pressed, the corresponding player's movement variable varlues are changed. 
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_a: 
                        if self.player.flip: 
                            if self.timer >=0 and self.timer < 20:
                                if self.boost_ready:
                                    self.boost_ready = False 
                                    self.player.dash()
                                else: 
                                    self.boost_ready = True 
                        else: 
                            self.boost_ready = True 
                        self.timer = 0
                        self.time_increment = True
                        self.player_movement[0] = True

                    if event.key == pygame.K_d: 
                        if not self.player.flip:
                            if self.timer >=0 and self.timer < 20:
                                if self.boost_ready: 
                                    self.boost_ready = False 
                                    self.player.dash()
                                else: 
                                    self.boost_ready = True 
                        else: 
                            self.boost_ready = True 
                        self.timer = 0
                        self.time_increment = True 
                        self.player_movement[1] = True
                        
                    if event.key == pygame.K_w:
                        self.player.player_jump() 
                    if event.key == pygame.K_s: 
                        self.player.slide = True 
                    if event.key == pygame.K_g: 
                        self.player.toggle_rapid_fire()

                        
                #define when the right or left arrow keys are then lifted, the corresponding player's movement variable values are changed back to false.
                if event.type == pygame.KEYUP: 

                    if event.key == pygame.K_a: 
                        self.player_movement[0] = False
                    if event.key == pygame.K_d:
                        self.player_movement[1] = False 
                    if event.key == pygame.K_s: 
                        self.player.slide =False 

            self.display_2.blit(self.display,(0,0))
            self.player.update_pos(self.Tilemap,self.cursor.pos,((self.player_movement[1]-self.player_movement[0])*self.PLAYER_DEFAULT_SPEED,0))
            self.player.render(self.display_2,render_scroll)
            

            self.screen.blit(pygame.transform.scale(self.display_2,self.screen.get_size()),(0,0))
            pygame.display.update()

            self.clock.tick(60)

myGame().run()