import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Knight_TeamA(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None
        self.can_heal = False

        self.graph = Graph(self)
        self.generate_pathfinding_graphs("knight_pathfinding_graph.txt")
        self.tower = []


        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.

        seeking_state = KnightStateSeeking_TeamA(self)
        attacking_state = KnightStateAttacking_TeamA(self)
        ko_state = KnightStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")
        

    def render(self, surface):
        # for i in range(len(self.world.graph.nodes)):
        #     pygame.draw.circle(surface, (0, 0, 0), (self.world.graph.nodes[i].position[0], self.world.graph.nodes[i].position[1]), int(5))
        #     font = pygame.font.SysFont("arial", 12, True)
        #     node_pos = font.render((str(self.world.graph.nodes[i].position)), True, (255, 255, 255))
        #     surface.blit(node_pos, self.world.graph.nodes[i].position)

        #     heal = font.render(str(self.can_heal), True, (255, 255, 255))
        #     surface.blit(heal, (self.position[0], self.position[1] + 30))

        for i in range(0, 33):
            if i == 12 or i == 27 or i ==28 or i ==21 or i == 22:
                continue
            pygame.draw.circle(surface, (0, 0, 0), (self.graph.nodes[i].position[0], self.graph.nodes[i].position[1]), int(5))
            font = pygame.font.SysFont("arial", 12, True)
            node_pos = font.render((str(self.graph.nodes[i].position)), True, (255, 255, 255))
            surface.blit(node_pos, self.graph.nodes[i].position)

        # pygame.draw.circle(surface, (255,0,0), (800, 685), int(5))
        # pygame.draw.circle(surface, (255,0,0), (940, 550), int(5))
        # pygame.draw.circle(surface, (255,0,0), (650, 555), int(5))
        # pygame.draw.circle(surface, (255,0,0), (740, 590), int(5))
        # pygame.draw.circle(surface, (255,0,0), (750, 440), int(5))
        # pygame.draw.circle(surface, (255,0,0), (840, 500), int(5))

        pygame.draw.circle(surface, (0, 0, 0), (int(self.position[0]), int(self.position[1])), int(self.min_target_distance), int(2))

        font = pygame.font.SysFont("arial", 12, True)
        state_name = font.render(self.brain.active_state.name, True, (255, 255, 255))
        surface.blit(state_name, self.position)

        if self.targeted:
            pygame.draw.line(surface, (0, 255, 0), self.position, self.targeted.position)
            pygame.draw.circle(surface, (255, 0, 0), (int(self.position[0]), int(self.position[1])), int(40), int(2))
        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)

        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown"]
        if self.can_level_up():
            print(self.xp)
            self.level_up(level_up_stats[0])

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
        
        self.paths = []
        line = f.readline()
        while line != "":
            path = Graph(self)
            data = line.split()

            #create nodes
            for i in range(0, len(data)):
                node = self.graph.nodes[int(data[i])]
                path.nodes[int(data[i])] = Node(path, int(data[i]), node.position[0], node.position[1])

            #create connections
            for i in range(0, len(data) - 1):
                node0 = int(data[i])
                node1 = int(data[i + 1])
                distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
                path.nodes[node0].addConnection(path.nodes[node1], distance)
                path.nodes[node1].addConnection(path.nodes[node0], distance)

            self.paths.append(path)

            line = f.readline()

        f.close()

    def get_enemy_tower(self, char):
        enemy_tower = []

        for entity in self.world.entities.values():
            if entity.team_id == 2 or entity.team_id == char.team_id:
                continue

            if entity.name == 'projectile' or entity.name == 'explosion':
                continue
            if entity.ko == True:
                continue
            if entity.name == 'tower':
                enemy_tower.append(entity.position)

        # print(enemy_tower)
        # print(self.tower)
        
        return enemy_tower

    def get_nearest_tower(self,char):
        nearest_tower = None
        distance = 0.
        heal_dist = self.maxSpeed * self.healing_cooldown
        print(heal_dist)
        
        for entity in self.world.entities.values():
            if entity.team_id == 2:
                continue
            if entity.team_id == char.team_id:
                continue
            if entity.name == "projectile" or entity.name == "explosion":
                continue
            if entity.name == "knight" or entity.name == "archer" or entity.name == "wizard" or entity.name == "orc":
                continue
            if entity.ko: 
                continue

            if nearest_tower is None:
                nearest_tower = entity
                distance = (char.position - entity.position).length()
            else:
                if distance > (char.position - entity.position).length():
                    distance = (char.position - entity.position).length()
                    nearest_tower = entity
                
        if (char.position - nearest_tower.position).length() > heal_dist:
            self.can_heal = True
        
        return nearest_tower

    def get_least_lane(self, char):

        orc_lane = {'0':0, '1':0, '2':0, '3':0}

        enemy_tower = char.get_enemy_tower(char)

        lane_with_least = None
        # print(parameter)

        for entity in self.world.entities.values():

            if entity.team_id == char.team_id or entity.team_id ==2 :
                continue
            
            if entity.name == 'orc':
                enemy_orc = entity
                enemy_path = enemy_orc.brain.states['seeking'].path_graph
                for i in range(0, len(self.world.paths)):
                    if enemy_path == self.world.paths[i]:
                    #    print(list(orc_lane.values())[i])
                    #    print("orc", orc_lane[str(i)])
                        orc_lane[str(i)] += enemy_orc.melee_damage #if target is tower
                        # orc_lane[str(i)] += 1 #if target is orcs

            if entity.name == 'knight' or entity.name == 'archer' or entity.name == 'wizard':
                enemy = entity
                enemy_path2 = enemy.path_graph
                for i in range(0, len(self.world.paths)):
                    if enemy_path2 == self.world.paths[i]:
                        orc_lane[str(i)] += enemy.melee_damage #if target is tower
                        # orc_lane[str(i)] += 100 #if target is orcs
    
        # if len(enemy_tower) == 2 or len(enemy_tower) == 0:
        if len(enemy_tower) == 2:
            for key in orc_lane.keys():
                if orc_lane[key] == min(orc_lane.values()):
                    lane_with_least = self.paths[int(key)]
                    # print("lane_values", orc_lane.values(), "key", key)
                continue
        else:
            self.archer = char.get_own_archer(char)
            lane_with_least = self.paths[0]
            # if (enemy_tower[0][0] <= char.tower[0][0]):
            #     lane_with_least = self.world.paths[0]
            # else:
            #     lane_with_least = self.world.paths[1]

        print("lane least", lane_with_least)
        # print(lane_with_least)
        # print("orc lane", orc_lane)
        return lane_with_least

    # def targeted(self, char):


class KnightStateSeeking_TeamA(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight

        self.knight.path_graph = self.knight.world.paths[randint(0, len(self.knight.world.paths)-1)]


    def do_actions(self):

        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        if self.can_heal:
            self.knight.heal()
            self.can_heal = False

        # check if opponent is in range
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
        if nearest_opponent is not None:
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                    self.knight.target = nearest_opponent
                    return "attacking"
        
        if (self.knight.position - self.knight.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None


    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)

        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position

        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


class KnightStateAttacking_TeamA(State):

    def __init__(self, knight):

        State.__init__(self, "attacking")
        self.knight = knight

    def do_actions(self):

        # colliding with target
        if pygame.sprite.collide_rect(self.knight, self.knight.target):
            self.knight.velocity = Vector2(0, 0)
            self.knight.melee_attack(self.knight.target)

        else:
            self.knight.velocity = self.knight.target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.knight.world.get(self.knight.target.id) is None or self.knight.target.ko:
            self.knight.target = None
            return "seeking"
            
        return None

    def entry_actions(self):

        return None


class KnightStateKO_TeamA(State):

    def __init__(self, knight):

        State.__init__(self, "ko")
        self.knight = knight

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.knight.current_respawn_time <= 0:
            self.knight.current_respawn_time = self.knight.respawn_time
            self.knight.ko = False
            self.knight.path_graph = self.knight.world.paths[randint(0, len(self.knight.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None
