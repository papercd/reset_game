#alright, now to what I think is the most questionable part of this session. 
#adding a tilemap. If I were to create a tilemap class, I would 
#have an iterable of some kind containing all the tiles, and the tiles 
#would be defined by the type of tiles it is, the variant of type it is, 
#and the position that it is supposed to have. So let's define that.
#Now the idea that pops into mind is to create a tile class, 
#then create another class called the tilemap class which is effectively 
#a list of the tile objects. 
import json 

import pygame 

PHYSICS_APPLIED_TILE_TYPES = {'grass','stone','box'}
AUTOTILE_TYPES = {'grass','stone'}
BULLET_TILE_OFFSET = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)]
SURROUNDING_TILE_OFFSET = [(1,0),(1,-1),(0,-1),(0,0),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)]


#variant rules that we expect to see depending on what side of the tile is empty. 

AUTOTILE_MAP ={
    tuple(sorted([(1,0),(0,1)])) : 0,
    tuple(sorted([(1,0),(0,1),(-1,0)])) : 1,
    tuple(sorted([(-1,0),(0,1)])) : 2,
    tuple(sorted([(-1,0),(0,-1),(0,1)])) :3,
    tuple(sorted([(-1,0),(0,-1)])) : 4,
    tuple(sorted([(-1,0),(0,-1),(1,0)])) :5,
    tuple(sorted([(1,0),(0,-1)])) :6,
    tuple(sorted([(1,0),(0,-1),(0,1)])) :7,
    tuple(sorted([(1,0),(-1,0),(0,1),(0,-1)])) :8
}



class Tilemap: 
    def __init__(self,game,tile_size = 16):
        self.tile_size = tile_size
        self.game = game
        
        self.enemies = []
        self.bullets = []

        self.tilemap = {}
        
        self.offgrid_tiles = [] 


    def json_seriable(self):
        seriable_tilemap = {}
        for key in self.tilemap: 
            tile = self.tilemap[key]
            seriable_tilemap[str(tile.pos[0]) +';' + str(tile.pos[1])] = {'type': tile.type,'variant' : tile.variant, 'pos' : tile.pos}
        
        seriable_offgrid = []
        for tile in self.offgrid_tiles:
            seriable_offgrid.append({'type': tile.type,'variant' : tile.variant, 'pos' : tile.pos})

        return seriable_tilemap,seriable_offgrid

    def generate(self):
        pass 

    def save(self,path):
        f = open(path,'w')
        tilemap,offgrid = self.json_seriable()
        

        json.dump({'tilemap': tilemap, 'tile_size': self.tile_size, 'offgrid':offgrid},f)
        f.close

    def load(self,path):
        f = open(path,'r')
        tilemap_data = json.load(f)

        for tile_key in tilemap_data['tilemap']:
            self.tilemap[tile_key] = Tile(tilemap_data['tilemap'][tile_key]["type"],tilemap_data['tilemap'][tile_key]["variant"],tilemap_data['tilemap'][tile_key]["pos"] )
        for tile_value in tilemap_data['offgrid']:
            self.offgrid_tiles.append(Tile(tile_value["type"],tile_value["variant"],tile_value["pos"]))

        f.close
    
    def extract(self,id_pairs,keep = False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile.type,tile.variant) in id_pairs: 
                matches.append(tile)
                if not keep: 
                    self.offgrid_tiles.remove(tile)

        copy_tilemap = self.tilemap.copy()
        for loc in copy_tilemap: 
            tile = copy_tilemap[loc]
            if (tile.type,tile.variant) in id_pairs:
                matches.append(tile)
                matches[-1].pos = matches[-1].pos.copy()
                matches[-1].pos[0] *= self.tile_size
                matches[-1].pos[1] *= self.tile_size
                if not keep: 
                    del self.tilemap[loc]
        return matches
  

    def tiles_around(self,pos,size):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),int(pos[1] // self.tile_size))
        #surrounding tile offset needs to be changed according to sprite size 
        x_bound = size[0]-1 // 16
        y_bound = size[1]-1 //16
        
        for x_cor in range(-1,x_bound +2):
            for y_cor in range(-1,y_bound +2):
                check_loc = str(tile_loc[0]+ x_cor) + ';' + str(tile_loc[1]+ y_cor)
                if check_loc in self.tilemap: 
                    tiles.append(self.tilemap[check_loc])
        return tiles 
                
    
    #this function will return the list of rectangles(grids) that surround a given position.
    #We want this function to select out the grids that we want to apply physics onto, so in this case, only 
    # when the grid is solid, grass or stone. 
    
    
    def grounded_enemeis_return_path(self,pos,size,dir,goal):

        size_in_tiles = (size[0]//self.tile_size,size[1]//self.tile_size)
        infront_tile_offset = self.tile_size #1 if (size[0] - size_in_tiles[0] * self.tile_size <  self.tile_size//2) else self.tile_size//2
        starting_nodes =[]
        nodes = []
       


        #I guess you can do that here. 
        for start_tile_pos in [-2*self.tile_size,-1*self.tile_size,0*self.tile_size,1*self.tile_size,2*self.tile_size]:

            loc = [pos[0]+infront_tile_offset,pos[1]+start_tile_pos]
            below_loc = [pos[0]+infront_tile_offset,pos[1]+start_tile_pos+self.tile_size]
            if not self.solid_check(loc) :
                if self.solid_check(below_loc):
                    starting_nodes.append(loc)
                        
       
        """     
        if not goal: 
            for y_cor in range(-2,3):
                if not dir:
                    
                    
                    for x_cor in range(0,3):
                        
                        loc = [pos[0]+ x_cor*self.tile_size,pos[1]+y_cor*self.tile_size]
                        #tile_loc = str(int(pos[0]//self.tile_size)+x_cor) + ';' + str(int(pos[1]//self.tile_size)+y_cor)
                        if not self.solid_check(loc):
                            loc[1] += self.tile_size
                            if self.solid_check(loc):
                                loc[1] -=self.tile_size
                                
                                
                                nodes.append(loc)
                        
                    

                else: 
                    starting_nodes =[]
                    #same here. 
                    
                    for x_cor in range(0,-3):
                        
                        loc = [pos[0]+ x_cor*self.tile_size,pos[1]+y_cor*self.tile_size]
                        #tile_loc = str(int(pos[0]//self.tile_size)+x_cor) + ';' + str(int(pos[1]//self.tile_size)+y_cor)
                        if not self.solid_check(loc):
                            loc[1] += self.tile_size
                            if self.solid_check(loc):
                                loc[1] -=self.tile_size
                                
                                nodes.append(loc)
                    

        """
        return starting_nodes 
    
    def find_next_node(self):
        #nodes on the edge: go down and if empty, add a node to the bottom. continue until you meet a solid tile. 
        pass 

    def physics_rects_around(self, pos,size):
        rects = []
        for tile in self.tiles_around(pos,size):
            if tile.type in PHYSICS_APPLIED_TILE_TYPES:
                rect = pygame.Rect(tile.pos[0]*self.tile_size,tile.pos[1]*self.tile_size,self.tile_size,self.tile_size) 
                rects.append(rect)
        return rects 
    
    def solid_check(self,pos):
        tile_loc = str(int(pos[0]//self.tile_size)) + ';' + str(int(pos[1]//self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc].type in PHYSICS_APPLIED_TILE_TYPES:
                return self.tilemap[tile_loc]

    def return_tile(self,rect):
        tile_key = str(rect.left//self.tile_size) + ';' + str(rect.top//self.tile_size)
        return self.tilemap[tile_key]


    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors= set()
            for side in [(1,0),(-1,0),(0,-1),(0,1)]:
                check_loc = str(tile.pos[0]+side[0]) +';' + str(tile.pos[1]+side[1])
                if check_loc in self.tilemap: 
                    if self.tilemap[check_loc].type == tile.type: 
                        neighbors.add(side)
            neighbors = tuple(sorted(neighbors))
            if tile.type in AUTOTILE_TYPES and neighbors in AUTOTILE_MAP:
                tile.variant = AUTOTILE_MAP[neighbors]



    def render(self, surf, offset = (0,0)):


        for x_cor in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size +1):
            for y_cor in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size +1): 
                coor = str(x_cor) + ';' + str(y_cor)
                if coor in self.tilemap: 
                    tile = self.tilemap[coor]
                    surf.blit(self.game.assets[tile.type][tile.variant],(tile.pos[0] * self.tile_size-offset[0], tile.pos[1] *self.tile_size-offset[1]))


        for tile in self.offgrid_tiles: 
            surf.blit(self.game.assets[tile.type][tile.variant], (tile.pos[0] - offset[0],tile.pos[1]-offset[1]))
        
        
class Tile: 
    def __init__(self,type,variant,pos):
        self.type = type 
        self.variant = variant
        self.pos = pos 
    
    def drop_item(self):
        if self.type == 'box':
            #this is where you implement the item drop system. 
            print('item_dropped')

class Node: 
    def __init__(self,pos):
        self.pos = pos 
        self.direction_x = 0
        self.direction_y = 0