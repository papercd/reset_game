#alright, now to what I think is the most questionable part of this session. 
#adding a tilemap. If I were to create a tilemap class, I would 
#have an iterable of some kind containing all the tiles, and the tiles 
#would be defined by the type of tiles it is, the variant of type it is, 
#and the position that it is supposed to have. So let's define that.
#Now the idea that pops into mind is to create a tile class, 
#then create another class called the tilemap class which is effectively 
#a list of the tile objects. 
import json 
import math
from queue import PriorityQueue
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
        
        self.path_graph = {}


    def json_seriable(self):
        seriable_tilemap = {}
        for key in self.tilemap: 
            tile = self.tilemap[key]
            seriable_tilemap[str(tile.pos[0]) +';' + str(tile.pos[1])] = {'type': tile.type,'variant' : tile.variant, 'pos' : tile.pos}
        
        seriable_offgrid = []
        for tile in self.offgrid_tiles:
            seriable_offgrid.append({'type': tile.type,'variant' : tile.variant, 'pos' : tile.pos})

        return seriable_tilemap,seriable_offgrid


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

        #create the path graph here. 
    
        

            

        f.close

    def graph_between_ent_player(self,ent_pos,player_pos):

        grid = {}
        
        ent_tile_pos = (ent_pos[0]//self.tile_size, ent_pos[1]//self.tile_size)
        player_tile_pos = (player_pos[0]//self.tile_size, player_pos[1]//self.tile_size)

        offset = (player_tile_pos[0] - ent_tile_pos[0],player_tile_pos[1] - ent_tile_pos[1])
        
        
           
        for y_cor in range(int(offset[1]) - 8 if int(offset[1]) <=0 else -8, 8 if int(offset[1]) <= 0 else int(offset[1]) + 8,1):
            for x_cor in range(0,int(offset[0]) + (6 if offset[0] >= 0 else -6),1 if offset[0] >= 0 else -1):
            

                tile_loc =  (ent_tile_pos[0] + x_cor,ent_tile_pos[1] + y_cor)
                tile_loc_check = str(int(tile_loc[0])) + ';' +str(int(tile_loc[1]))  
                
                if tile_loc_check not in self.tilemap:
                    
                    below_tile_loc = (tile_loc[0],tile_loc[1]+1)
                    below_tile_loc_check = str(int(below_tile_loc[0])) + ';' + str(int(below_tile_loc[1]))

                    if below_tile_loc_check in self.tilemap: 
                        
                        grid[tile_loc] = Node(tile_loc)
                        
                        #check for connections. 
                        
                        if offset[0] >=0:
                            
                            left_loc = (tile_loc[0]-1,tile_loc[1])
                            left_loc_check = str(int(left_loc[0])) + ';' + str(int(left_loc[1]))

                            #up_loc = (tile_loc[0],tile_loc[1]-1)
                            #up_loc_check = str(int(up_loc[0])) + ';' + str(int(up_loc[1]))

                            if left_loc in grid: 
                                grid[left_loc].right = grid[tile_loc]
                                grid[tile_loc].left = grid[left_loc]
                            elif left_loc_check in self.tilemap: 
                                # if there is no node on the left side, then check for a tile instead. 
                                
                                #if there is a tile there, then add the connection. 
                                grid[tile_loc].left = self.tilemap[left_loc_check]

                            """
                            if up_loc in grid: 
                                grid[up_loc].neighbors.append(grid[tile_loc])
                                grid[tile_loc].neighbors.append(grid[up_loc])
                            """
                            
                        else: 
                            
                            right_loc = (tile_loc[0]+1,tile_loc[1])
                            right_loc_check = str(int(right_loc[0])) + ';' + str(int(right_loc[1]))

                            #up_loc = (tile_loc[0],tile_loc[1]-1)
                            #up_loc_check = str(int(up_loc[0])) + ';' + str(int(up_loc[1]))

                            if right_loc in grid: 
                                grid[right_loc].left = grid[tile_loc]
                                grid[tile_loc].right = grid[right_loc]

                            elif right_loc_check in self.tilemap:
                    
                                #if there is a tile to the right, then add the connection.
                                grid[tile_loc].right = self.tilemap[right_loc_check]
                            """
                            if up_loc in grid: 
                                grid[up_loc].neighbors.append(grid[tile_loc])
                                grid[tile_loc].neighbors.append(grid[up_loc])
                            """
                            
        
        #now, for the jump nodes. 
        
        airborne_grid = {}

        for key in grid: 
            node = grid[key]
            if node.left == None: 
                #if there is no left neighbor: 
                #add a node there. 

                new_node_loc = (node.pos[0] -1 , node.pos[1])
                new_node = Node(new_node_loc)

                node.left = new_node 
                new_node.right = node 
                
                #check for downward connections. and continue on doing it until you reach another node or a tile. 
                self.recursion_depth = 0
                new_node.down = self.downward_connection(new_node,grid,airborne_grid)

                #once you've added all the connections, add the node to the grid. 
                airborne_grid[new_node_loc] = new_node
                
                
            if node.right == None: 
                #if there is no up neighbor: 
                new_node_loc = (node.pos[0] +1 , node.pos[1])
                new_node = Node(new_node_loc)

                node.right = new_node 
                new_node.left = node 
                
                #check for downward connections. and continue on doing it until you reach another node or a tile. 
                self.recursion_depth = 0
                new_node.down = self.downward_connection(new_node,grid,airborne_grid)

                #once you've added all the connections, add the node to the grid. 
                airborne_grid[new_node_loc] = new_node
        
        for key in airborne_grid: 
            node = airborne_grid[key]
            grid[key] = node 
        
        return grid
           
        
                 
    def downward_connection(self,node,grid,airborne_grid):
        if self.recursion_depth >= 15:
            return None
        else: 
            #check for the position below the given node. 
            below_loc = (int(node.pos[0]),int(node.pos[1]+1))
            below_loc_check = str(below_loc[0]) + ';' + str(below_loc[1])

            if below_loc_check not in self.tilemap and below_loc not in grid and below_loc not in airborne_grid:
                #if the space below is empty, then create a node and continue the downard connection. 
                new_node = Node(below_loc)
                new_node.up = node 

                self.recursion_depth +=1
                airborne_grid[below_loc] = new_node 
                new_node.down = self.downward_connection(new_node,grid,airborne_grid)
                
                return new_node 
            elif below_loc_check in self.tilemap: 
                #if the space below has a tile, 
                return self.tilemap[below_loc_check]
            elif below_loc in grid: 
                #if the space below is another node, 
                grid[below_loc].up = node 
                return grid[below_loc]
            else: 
                #if the space below is another airborne node 
                airborne_grid[below_loc].up  = node 
                return airborne_grid[below_loc]


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

        
        """
        for key in graph:
            node = graph[key]
            test_surf = pygame.Surface((2,2))
            surf.blit(test_surf,(node.pos[0] * self.tile_size - offset[0] + 8,node.pos[1] * self.tile_size - offset[1]+ 4))
        """
        
        
class Tile: 
    def __init__(self,type,variant,pos):
        self.type = type 
        self.variant = variant
        self.pos = pos 
   
    def drop_item(self):
        if self.type == 'box':
            print('item_dropped')

class Node: 
    def __init__(self,pos):
        self.pos = pos
        #neighbors save position values of neighboring nodes. 
        self.left = None
        self.right = None 
        self.up = None
        self.down = None 
        self.x_dir = 0
        self.y_dir = 0
    
   

class Graph_between_ent_and_player: 

    def __init__(self,tilemap):
        self.tilemap = tilemap
        self.graph = {}


    def update(self):
        self.graph = {}
        x_cors = []
        y_cors = []

        for key in self.tilemap.tilemap: 
            tile = self.tilemap.tilemap[key] 
            
            x_cors.append(tile.pos[0])
            y_cors.append(tile.pos[1])
        
        x_cors =sorted(x_cors)
        y_cors =sorted(y_cors)        

        for x in range(x_cors[0]-50,x_cors[-1]+50):
            for y in range(y_cors[0]-50,y_cors[-1]+50):
               
                tile_loc = (x,y)
                tile_loc_check = str(tile_loc[0]) + ';' +str(tile_loc[1])  

                if tile_loc_check not in self.tilemap.tilemap:
                
                    #then you create a node. 
                    self.graph[tile_loc_check] = Node(tile_loc)  
                    left_check = str(tile_loc[0]-1) + ';' + str(tile_loc[1]) 
        
                    #check for left connection
                    if left_check in self.graph: 
                        #if there is a node to the left, add the connections. 
                        self.graph[tile_loc_check].neighbors.append(self.graph[left_check])
                        self.graph[left_check].neighbors.append(self.graph[tile_loc_check])

                """    
                down_tile_loc = (tile_loc[0], tile_loc[1]+1) 
                down_tile_loc_check = str(down_tile_loc[0]) + ';' +str(down_tile_loc[1])  
                

                if down_tile_loc_check in self.tilemap.tilemap: 
                """




    def return_graph(self):
        return self.graph        


