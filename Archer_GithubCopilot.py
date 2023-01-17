from random import randint, random

import pygame
import math

from Character import *
from Graph import *
from State import *


class Archer_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None
        self.lane = None

        #Checks if archer is going to reset point
        self.resetting = False

        #Path initialization
        self.graph = Graph(self)
        self.generate_pathfinding_graphs("archer_pathfinding.txt")
        self.reset_points = [Vector2(310, 80), Vector2(484, 80), Vector2(705,71), Vector2(870,80), #Top Lane
                            Vector2(925,390), Vector2(876,508), Vector2(940, 190), Vector2(943,294),#Top Lane
                            Vector2(90,390), Vector2(80,520), Vector2(180,670), Vector2(447,721), Vector2(630, 710), Vector2(755, 680)] #Bot Lane

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = ArcherStateSeeking_TeamA(self)
        attacking_state = ArcherStateAttacking_TeamA(self)
        dodgeEnemy_state = ArcherStateDodgeEnemy_TeamA(self)
        ko_state = ArcherStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(dodgeEnemy_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)
        if DEBUG:
            self.graph.render(surface)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.move_target.position[0]), int(self.move_target.position[1])), int(5), int(4))
            for point in self.reset_points:
                pygame.draw.circle(surface, (0, 0, 255), (int(point[0]), int(point[1])), int(5), int(4))


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        # level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        level_up_stats = ["ranged cooldown", "speed", "ranged damage"]
        if self.can_level_up():
            choice = randint(0, 2)
            self.level_up(level_up_stats[choice])   


    # --- Reads a set of pathfinding graphs from a file ---
    def generate_pathfinding_graphs(self, filename):

        f = open(filename, "r")

        # Create the nodes
        line = f.readline() 
        while line != "connections\n":
            data = line.split()
            self.graph.nodes[int(data[0])] = Node(self.graph, int(data[0]), int(data[1]), int(data[2]))
            line = f.readline()

        # Create the connections
        line = f.readline()
        while line != "paths\n":
            data = line.split()
            node0 = int(data[0])
            node1 = int(data[1])
            distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
            self.graph.nodes[node0].addConnection(self.graph.nodes[node1], distance)
            self.graph.nodes[node1].addConnection(self.graph.nodes[node0], distance)
            line = f.readline()

        # Create the orc paths, which are also Graphs
        self.paths = []
        line = f.readline()
        while line != "":
            path = Graph(self)
            data = line.split()
            
            # Create the nodes
            for i in range(0, len(data)):
                node = self.graph.nodes[int(data[i])]
                path.nodes[int(data[i])] = Node(path, int(data[i]), node.position[0], node.position[1])

            # Create the connections
            for i in range(0, len(data)-1):
                node0 = int(data[i])
                node1 = int(data[i + 1])
                distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
                path.nodes[node0].addConnection(path.nodes[node1], distance)
                path.nodes[node1].addConnection(path.nodes[node0], distance)
                
            self.paths.append(path)

            line = f.readline()

        f.close()


    #Sets velocity, normalize ip for archer
    def set_velocity(self, target): #Target type: Vector2()
        self.velocity = target - self.position
        if self.velocity.length() > 0:
                self.velocity.normalize_ip();
                self.velocity *= self.maxSpeed


    def reached_boundary(self):
        
        #Check if touches base or obstacle
        collision_list = pygame.sprite.spritecollide(self, self.world.obstacles, False, pygame.sprite.collide_mask)
        for entity in collision_list:
            if entity.name == "obstacle":
                return True

        return False


    def get_nearest_reset(self):
        nearest = None
        distance = 99999999999999

        for point in self.reset_points:
            if (point - self.position).length() < distance:
                nearest = point
                distance = (self.position - point).length()

        return nearest
    

    #Returns nearest edge to the character
    def nearest_edge(self):

        #Left edge
        nearestLen = self.position[0]
        nearest = "left"

        #Right edge
        if SCREEN_WIDTH - self.position[0] < nearestLen:
            nearestLen = SCREEN_WIDTH - self.position[0]
            nearest = "right"

        #Top edge
        if self.position[1] < nearestLen:
            nearestLen = self.position[1]
            nearest = "up"
        
        #Bottom edge
        if SCREEN_HEIGHT - self.position[1] < nearestLen:
            nearestLen = SCREEN_HEIGHT - self.position[1]
            nearest = "down"

        return nearest


    #Check if archer should shift to dodgeTower state
    def to_dodgeTower(self):
        for entity in self.world.entities.values():
            if entity.team_id != self.team_id and entity.name == "tower":
                #Check if archer is in range of enemy to dodge
                if (self.position - entity.position).length() <= self.min_target_distance:
                    self.target = entity
                    return True
        
        return False


class ArcherStateSeeking_TeamA(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        #Goes to top lane
        self.archer.path_graph = self.archer.paths[0]
        self.archer.lane = "top"


    def do_actions(self):

        self.archer.set_velocity(self.archer.move_target.position)


    def check_conditions(self):

        if self.archer.current_hp/self.archer.max_hp < 0.7:
            self.archer.heal()

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"
    
        # Go to dodgeTower state
        if self.archer.to_dodgeTower():
            return "dodgeEnemy"

        #Resetting position takes priority so that archer will not get stuck
        if not self.archer.resetting:
            if (self.archer.position - self.archer.move_target.position).length() < 8:

                # continue on path
                if self.current_connection < self.path_length:
                    self.archer.move_target.position = self.path[self.current_connection].toNode.position
                    self.current_connection += 1
        
        else:
            if (self.archer.position - self.archer.move_target.position).length() < 8:
                self.archer.resetting = False

        
        if self.archer.reached_boundary():
            self.archer.resetting = True
            self.archer.move_target.position = self.archer.get_nearest_reset()
                
        return None

    def entry_actions(self):
        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.target_node_index])
        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position


class ArcherStateAttacking_TeamA(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer
        self.dodging_archer = False
        self.move_up = False

    def do_actions(self):

        opponent_distance = (self.archer.position - self.archer.target.position).length()
        #Update nearest opponent
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if (self.archer.position - nearest_opponent.position).length() <= self.archer.min_target_distance:
            self.archer.target = nearest_opponent

        # opponent within range
        if opponent_distance <= self.archer.min_target_distance:
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position) 
        else:
            self.archer.move_target.position = self.archer.target.position

        self.archer.set_velocity(self.archer.move_target.position)


    def check_conditions(self):

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"

        opponent_distance = (self.archer.position - self.archer.target.position).length()

        #Resetting position takes priority so that archer will not get stuck
        if not self.archer.resetting:

            if self.archer.target.name in ["archer", "tower", "base", "wizard"]:
                return "dodgeEnemy"

            #Move backwards if opponent is within this distance
            if opponent_distance <= self.archer.min_target_distance - 40:

                #Set archer position to the path/roam around the base
                if self.current_connection < self.path_length:
                    self.archer.move_target.position = self.path[self.current_connection].toNode.position
                else:
                    self.archer.move_target.position = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)].connections[0].fromNode.position

            if (self.archer.position - self.archer.move_target.position).length() < 8:
                # continue on path
                if self.current_connection < self.path_length:   
                    self.archer.move_target.position = self.path[self.current_connection].toNode.position
                    self.current_connection += 1

        #Reached reset point                   
        else:
            if (self.archer.position - self.archer.move_target.position).length() < 8:
                self.archer.resetting = False

        #Reached a boundary (Edge of screen, or obstacle)
        if self.archer.reached_boundary():
            self.archer.resetting = True
            self.archer.move_target.position = self.archer.get_nearest_reset()

        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.spawn_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].toNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.spawn_node_index].position

        return None


class ArcherStateDodgeEnemy_TeamA(State):

    def __init__(self, archer):

        State.__init__(self, "dodgeEnemy")
        self.archer = archer
        self.wait = False
        self.move_count = 0

    def do_actions(self):

        #Update nearest opponent
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if (self.archer.position - nearest_opponent.position).length() <= self.archer.min_target_distance:
            if (nearest_opponent.name == "orc" or nearest_opponent.name == "knight") and \
                (self.archer.position - nearest_opponent.position).length() <= self.archer.min_target_distance - 50:
                self.archer.target = nearest_opponent

        self.archer.set_velocity(self.archer.move_target.position)

    def check_conditions(self):

        #Attack opponent if in range
        opponent_distance = (self.archer.position - self.archer.target.position).length()
        if opponent_distance <= self.archer.min_target_distance:
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)
        
        elif opponent_distance <= self.archer.min_target_distance:
            return "attacking"

        #Back to attacking state if target changes to knight or orc
        if self.archer.target.team_id != self.archer.team_id and self.archer.target.name in ["knight", "orc"]:
            return "attacking"

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"

        #Dodging mechanic
        if not self.wait:
            if (self.archer.position - self.archer.move_target.position).length() < 8:
                self.point_index += self.increment
                self.archer.move_target.position = self.move_list[self.point_index]
                self.move_count += 1

        else:
            self.archer.velocity = Vector2(0, 0)
            for entity in self.archer.world.entities.values():
                if entity.team_id != self.archer.team_id and entity.name == "projectile":
                    if (self.archer.position - entity.position).length() <= self.archer.min_target_distance:
                        self.wait = False      

        if self.move_count > 15:
            self.increment *= -1
            self.point_index += self.increment
            self.archer.move_target.position = self.move_list[self.point_index]
            self.move_count = 0

        if self.archer.move_target.position[0] <= 5 or self.archer.move_target.position[0] >= SCREEN_WIDTH - 5 or\
            self.archer.move_target.position[1] <= 5 or self.archer.move_target.position[1] >= SCREEN_HEIGHT - 5:
            self.increment *= -1
            self.point_index += self.increment
            self.archer.move_target.position = self.move_list[self.point_index]
            self.wait = True
            self.move_count = 0
        
        for entity in self.archer.world.entities.values():
            if entity.name == "obstacle":
                if entity.rect.collidepoint(self.move_list[self.point_index]):
                    self.increment *= -1
                    self.point_index += self.increment
                    self.archer.move_target.position = self.move_list[self.point_index]
                    self.wait = True
                    self.move_count = 0

    def entry_actions(self):

        #Similar logic as code in Wizard Attacking state, dodge in circular formation
        self.move_list = []
        point_dist = 10
        radius = self.archer.min_target_distance
        circumference = 2*math.pi*self.archer.min_target_distance
        point_count = int(circumference/point_dist)
        angle = 360/point_count

        #Generate points
        for i in range(point_count):
            x = self.archer.target.position[0] + radius * math.cos(math.radians(i*angle))
            y = self.archer.target.position[1] + radius * math.sin(math.radians(i*angle))

            pos = Vector2(x, y)
            self.move_list.append(Vector2(x, y))
    

        #Get closest point
        self.point_index = 0
        closest = 99999999
        for i in range(len(self.move_list)):
            if (self.archer.position - self.move_list[i]).length() < closest:
                closest = (self.archer.position - self.move_list[i]).length()
                self.point_index = i

        self.archer.move_target.position = self.move_list[self.point_index]
        self.increment = 1
        return None


class ArcherStateKO_TeamA(State):

    def __init__(self, archer):

        State.__init__(self, "ko")
        self.archer = archer

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.archer.current_respawn_time <= 0:
            self.archer.current_respawn_time = self.archer.respawn_time
            self.archer.ko = False
            self.archer.path_graph = self.archer.paths[0]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None
