
import json 
import pygame
import heapq


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

        f.close

    def graph_between_ent_player(self,ent_pos,player_pos):

        grid = {}
        
        ent_tile_pos = (ent_pos[0]//self.tile_size, ent_pos[1]//self.tile_size)
        player_tile_pos = (player_pos[0]//self.tile_size, player_pos[1]//self.tile_size)

        offset = (player_tile_pos[0] - ent_tile_pos[0],player_tile_pos[1] - ent_tile_pos[1])
        
        
           
        for y_cor in range(int(offset[1]) - 15 if int(offset[1]) <=0 else -15, 15 if int(offset[1]) <= 0 else int(offset[1]) + 15,1):
            for x_cor in range(-15 if offset[0] >= 0 else 15,int(offset[0]) + (15 if offset[0] >= 0 else -15),1 if offset[0] >= 0 else -1):
            

                tile_loc =  (int(ent_tile_pos[0] + x_cor),int(ent_tile_pos[1] + y_cor))
                tile_loc_check = str(tile_loc[0]) + ';' +str(tile_loc[1])  
                

                
                if tile_loc_check not in self.tilemap:
                    
                    below_tile_loc = (int(tile_loc[0]),int(tile_loc[1]+1))
                    below_tile_loc_check = str(below_tile_loc[0]) + ';' + str(below_tile_loc[1])

                    if below_tile_loc_check in self.tilemap: 
                        
                        new_node = Node(tile_loc)
                        new_node.down = self.tilemap[below_tile_loc_check]

                        grid[tile_loc] = new_node
                        
                        #check for connections. 
                        
                        if offset[0] >=0:
                            
                            left_loc = (tile_loc[0]-1,tile_loc[1])
                            left_loc_check = str(left_loc[0]) + ';' + str(left_loc[1])

                           

                            if left_loc in grid: 
                                grid[left_loc].right = grid[tile_loc]
                                grid[tile_loc].left = grid[left_loc]
                            elif left_loc_check in self.tilemap: 
                                grid[tile_loc].left = self.tilemap[left_loc_check]

                            
                        else: 
                            
                            right_loc = (tile_loc[0]+1,tile_loc[1])
                            right_loc_check = str(right_loc[0]) + ';' + str(right_loc[1])

                           

                            if right_loc in grid: 
                                grid[right_loc].left = grid[tile_loc]
                                grid[tile_loc].right = grid[right_loc]

                            elif right_loc_check in self.tilemap:
                    
                                
                                grid[tile_loc].right = self.tilemap[right_loc_check]
                            
                            
        
        #now, for the jump nodes. 
        
        airborne_grid = {}

        

        for key in grid: 
            node = grid[key]
            if not node.left : 
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
                
                
            if not node.right : 
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
        
        if ent_tile_pos not in grid and ent_tile_pos not in airborne_grid:
            #this means that the tile location of the enemy is empty, as well as the tile location beneath it. 
            new_node = Node(ent_tile_pos)
            self.recursion_depth = 0
            new_node.down = self.downward_connection(new_node,grid,airborne_grid)
            airborne_grid[ent_tile_pos] = new_node 

        if player_tile_pos not in grid and player_tile_pos not in airborne_grid:
            #this means that the tile location of the player is empty, as well as the tile location beneath it. 
            new_node = Node(player_tile_pos)
            self.recursion_depth = 0
            new_node.down = self.downward_connection(new_node,grid,airborne_grid)
            airborne_grid[player_tile_pos] = new_node 
            
            
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
            
    def Astar_pathfinding(self,start_pos,end_pos):
       
        graph = self.graph_between_ent_player(start_pos,end_pos)
        
        start_node = graph[(start_pos[0]//self.tile_size,start_pos[1]//self.tile_size)]
        end_node = graph[(end_pos[0]//self.tile_size,end_pos[1]//self.tile_size)]

        # Initialize the open and closed sets
        open_set = []
        closed_set = set()

        # Initialize the start node's g score to 0 and its f score to the heuristic estimate
        start_node.g = 0
        start_node.f = self.heuristic(start_node.pos, end_node.pos)

        # Add the start node to the open set
        heapq.heappush(open_set,(start_node.f, start_node))
        while open_set:
            # Pop the node with the lowest f score from the open set
            current_f, current_node = heapq.heappop(open_set)

            # If the current node is the goal, reconstruct the path and return it
            if current_node == end_node:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                
                return path[::-1]

            # Add the current node to the closed set
            closed_set.add(current_node)

            # Explore neighbors of the current node
            for neighbor_node in [current_node.left, current_node.right, current_node.up, current_node.down]:
                if neighbor_node is None or neighbor_node in closed_set:
                    continue
                if isinstance(neighbor_node,Tile):
                    continue
                # Calculate tentative g score
                tentative_g = current_node.g + 1

                # If the neighbor has not been evaluated yet or the new g score is lower
                if neighbor_node not in open_set or tentative_g < neighbor_node.g:
                    # Update neighbor's parent and g score
                    neighbor_node.parent = current_node
                    neighbor_node.g = tentative_g
                    neighbor_node.f = tentative_g + self.heuristic(neighbor_node.pos, end_pos)

                    # Add neighbor to the open set
                    heapq.heappush(open_set, (neighbor_node.f, neighbor_node))

        # If open set is empty and goal not reached, return empty path
        return []
    

        





    def heuristic(self, a, b):
        """
        Calculate the Manhattan distance heuristic between two points.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


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
    
    def return_color(self,rect):
        tile = self.return_tile(rect)
        tile_img = self.game.assets[tile.type][tile.variant]
        return tile_img.get_at((self.tile_size/2,self.tile_size/2))
    

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
            print('item_dropped')

class Node: 
    def __init__(self,pos):
        
        self.pos = pos
        self.left = None
        self.right = None 
        self.up = None
        self.down = None 
        self.parent = None 
        self.g = float('inf')
        self.f = float('inf')
        
    def __hash__(self):
        """
        Define a hash value based on the position attribute.
        """
        return hash(self.pos)
    def __lt__(self, other):
        """
        Define comparison for the less than operator.
        """
        return self.f < other.f

   
     


