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
        self.targeted = False

        self.follow = None
        self.hero = None

        self.graph = Graph(self)
        self.generate_pathfinding_graphs("knight_pathfinding_graph.txt")
        self.tower = []

        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.

        seeking_state = KnightStateSeeking_TeamA(self)
        attacking_state = KnightStateAttacking_TeamA(self)
        # follow_state = KnightStateFollow_TeamA(self)
        ko_state = KnightStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        # self.brain.add_state(follow_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")
        
        self.text = ""


    def render(self, surface):
        #uncomment

        if self.text != "":
            font = pygame.font.SysFont("arial", 12, True)
            follo = font.render(self.text, True, (255, 0, 0))
            surface.blit(follo, ((SCREEN_WIDTH/2 - follo.get_width()/2), (30)))

            #end
        # for i in range(len(self.world.graph.nodes)):
        #     pygame.draw.circle(surface, (0, 0, 0), (self.world.graph.nodes[i].position[0], self.world.graph.nodes[i].position[1]), int(5))
        #     font = pygame.font.SysFont("arial", 12, True)
        #     node_pos = font.render((str(self.world.graph.nodes[i].position)), True, (255, 255, 255))
        #     surface.blit(node_pos, self.world.graph.nodes[i].position)

        #     heal = font.render(str(self.can_heal), True, (255, 255, 255))
        #     surface.blit(heal, (self.position[0], self.position[1] + 30))

        #uncomment
        for i in range(0, 33):
            if i == 12 or i == 27 or i ==28 or i ==21 or i == 22:
                continue
            pygame.draw.circle(surface, (0, 0, 0), (self.graph.nodes[i].position[0], self.graph.nodes[i].position[1]), int(5))
            font = pygame.font.SysFont("arial", 12, True)
            node_pos = font.render((str(self.graph.nodes[i].position)), True, (255, 255, 255))
            surface.blit(node_pos, self.graph.nodes[i].position)
        #end

        # pygame.draw.circle(surface, (255,0,0), (800, 685), int(5))
        # pygame.draw.circle(surface, (255,0,0), (940, 550), int(5))
        # pygame.draw.circle(surface, (255,0,0), (650, 555), int(5))
        pygame.draw.circle(surface, (255,0,0), (660, 700), int(5))
        pygame.draw.circle(surface, (255,0,0), (910, 410), int(5))
        pygame.draw.line(surface, (255, 0, 0), (660,410), (1024, 410))
        pygame.draw.line(surface, (255, 0, 0), (660, 410), (660, 768))
        # pygame.draw.circle(surface, (255,0,0), (int(self.position[0]), int(self.position[1])), int(10), int(2))

        #uncomment
        pygame.draw.circle(surface, (0, 0, 0), (int(self.position[0]), int(self.position[1])), int(self.min_target_distance), int(2))

        font = pygame.font.SysFont("arial", 15, True)
        state_name = font.render((self.brain.active_state.name + self.follow), True, (255, 255, 255))
        surface.blit(state_name, ((SCREEN_WIDTH/2 - state_name.get_width()/2), (30)))

        if self.targeted:
            pygame.draw.line(surface, (0, 255, 0), self.position, self.targeted.position)
            pygame.draw.circle(surface, (255, 0, 0), (int(self.position[0]), int(self.position[1])), int(40), int(2))
        #end
        Character.render(self, surface)

    def process(self, time_passed):
        
        Character.process(self, time_passed)

        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown"]
        if self.can_level_up():
            print(self.xp)
            level = self.xp/100
            if level < 4:            
                self.level_up("hp")
            else:
                if randint(0, 100) < 50:
                    self.level_up("melee damage")
                else: 
                    self.level_up("melee cooldown")

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
                enemy_tower.append(entity)

        # print(enemy_tower)
        # print(self.tower)
        
        return enemy_tower

    def get_nearest_enemy(self,char):
        nearest_tower = None
        entity_around_list = []
        main_target_list = []
        distance = 0.
        
        for entity in self.world.entities.values():
            if entity.team_id == 2:
                continue
            if entity.team_id == char.team_id:
                continue
            if entity.name == "projectile" or entity.name == "explosion":
                continue
            # if entity.name == "knight" or entity.name == "archer" or entity.name == "wizard" or entity.name == "orc":
                # continue
            if (char.position - entity.position).length() > char.min_target_distance:
                continue
            if entity.ko: 
                continue
            
            if entity.name == "base" or entity.name == "tower":
                main_target_list.append(entity)
            else:
                entity_around_list.append(entity)
            
        if main_target_list == []:
            for entity in entity_around_list:
                if entity.name == "wizard":
                    return entity
                elif entity.name == "archer":
                    return entity
                elif entity.name == "knight":
                    return entity
                else:
                    if nearest_tower is None:
                        nearest_tower = entity
                        distance = (char.position - entity.position).length()
                        
                    else:
                        if distance > (char.position - entity.position).length():
                            distance = (char.position - entity.position).length()
                            nearest_tower = entity
        else: 
            for entity in main_target_list:
                if nearest_tower is None:
                        nearest_tower = entity
                        distance = (char.position - entity.position).length()
                else:
                    if distance > (char.position - entity.position).length():
                        distance = (char.position - entity.position).length()
                        nearest_tower = entity
        
        return nearest_tower

    def get_least_lane(self, char):

        orc_lane = {'0':0, '1':0, '2':0, '3':0}

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
        
        for key in orc_lane.keys():
            if orc_lane[key] == min(orc_lane.values()):
                lane_with_least = self.paths[int(key)]

        print("lane least", lane_with_least)
        # print(lane_with_least)
        # print("orc lane", orc_lane)
        return lane_with_least

    def get_lane(self, char):
        lane = None

        enemy_tower = char.get_enemy_tower(char)

        # if len(enemy_tower) == 2 or len(enemy_tower) == 0:
        if len(enemy_tower) == 2 or (len(enemy_tower) == 0 and char.base.current_hp == BASE_MAX_HP):
            char.follow = "wizard"
        else:
            char.follow = "archer"

        if char.follow != None:
            for entity in self.world.entities.values():
                if entity.team_id == 2 or entity.team_id != char.team_id:
                    continue
                if entity.name == char.follow:
                    for i in range(len(self.world.paths)):
                        if self.world.paths[i] == entity.path_graph:
                            lane = char.paths[i]
                            self.hero = entity
                            continue
                if lane == None:
                    lane = char.paths[0]
        
        if char.follow == None or lane == None:
            lane = char.get_least_lane(char)
        
        self.text = "Follow " + str(char.follow)
        print(self.text)
        return lane

    def get_entity(self, entity_name, team): 
        for entity in self.world.entities.values():
            if entity.team_id == 2 or entity.team_id == team:
                continue
            if entity.name == entity_name:
                return entity
        return None

    def reset(self, hero):
        if hero == None:
            self.velocity = self.path_graph.get_nearest_node(self.position).position - self.position
            if self.velocity.length() > 0:
                self.velocity.normalize_ip();
                self.velocity *= self.maxSpeed
            
            self.move_target.position = self.path_graph.get_nearest_node(self.position).position
            
        else:
            self.velocity = hero.position - self.position
            if self.velocity > hero.projectile_range:
                self.velocity = self.path_graph.get_nearest_node(self.position).position - self.position
            else:
                self.move_target.position = hero.position

            if self.velocity.length() > 0:
                    self.velocity.normalize_ip()
                    self.velocity *= self.maxSpeed

    def colliding(self, char):
        collide_list = pygame.sprite.spritecollide(self, self.world.obstacles, False, pygame.sprite.collide_mask)
        for entity in collide_list:
            if char.target != entity:
                if entity.name == 'obstacle' or entity.name == 'tower' or entity.name == 'base':
                    
                    char.text = "colliding"
                    return True
        char.text = ""
        return False

    def move_back(self, char):
        # top = char.position[1] <= SCREEN_HEIGHT/7
        # bottom = char.position[1] >=SCREEN_HEIGHT - SCREEN_HEIGHT/7
        # left = char.position[0] <= SCREEN_WIDTH/9
        # right = char.position[0] >= SCREEN_WIDTH - SCREEN_WIDTH/9

        # if top or bottom:
        #     char.velocity = char.position - Vector2(10,0)
        # elif left or right:
        #     char.velocity = char.position - Vector2(0, 10)

        if char.position[0] < char.target.position[0] and char.position[1] > char.target.position[1]:
            char.move_target.position = char.position + Vector2(5, 0)
        elif char.position[0] > char.target.position[0] and char.position[1] < char.target.position[1]:
            char.move_target.position = char.position + Vector2(0, 5)
        elif char.position[0] == char.target.position[0] and char.position[1] < char.target.position[1]:
            char.move_target.position = char.position + Vector2(5, 0)
        elif char.position[0] < char.target.position[0] and char.position[1] == char.target.position[1]:
            char.move_target.position = char.position + Vector2(0, 5)
        elif char.position[0] > char.target.position[0] and char.position[1] > char.target.position[1]:
            char.move_target.position = char.position + Vector2(5, 0)
        elif char.position[0] < char.target.position[0] and char.position[1] > char.target.position[1]:
            char.move_target.position = char.position + Vector2(5, 0)
        elif char.position[0] == char.target.position[0] and char.position[1] > char.target.position[1]:
            char.move_target.position = char.position + Vector2(5, 0)
        elif char.position[0] > char.target.position[0] and char.position[1] == char.target.position[1]:
            char.move_target.position = char.position + Vector2(0, 5)
        
        char.velocity = char.position - char.move_target.position
        if char.velocity.length() > 0:
            char.velocity.normalize_ip()
            char.velocity *= char.maxSpeed    

    def enemy_around(self, char):
        enemy_list = []

        for entity in self.world.entities.values():
            if entity.team_id == 2 or entity.team_id == char.team_id:
                continue
            
    def get_enemy_rect(self, char):
        enemy_tower_radius = [364, 358]
        enemy_rect = []

        if char.base.position[0] < SCREEN_WIDTH/2:
            x_val = SCREEN_WIDTH - enemy_tower_radius[0]
            y_val = SCREEN_HEIGHT - enemy_tower_radius[1]
        elif char.base.position[0] > SCREEN_WIDTH/2:
            x_val = enemy_tower_radius[0]
            y_val = enemy_tower_radius[1]

        x = x_val
        y = y_val

        for tower in char.tower:

            if tower.position[0] < SCREEN_WIDTH/2:
                x_val = tower.position[0] + tower.min_target_distance
                y_val = tower.position[1] + tower.min_target_distance
            else:
                x_val = tower.position[0] - tower.min_target_distance
                y_val = tower.position[1] - tower.min_target_distance
            
            if x == None and y == None:
                x = x_val
                y = y_val
            elif x_val < x:
                x = x_val
            elif y_val < y:
                y = y_val

        enemy_rect = [x_val, y_val]

        return enemy_rect
       
    def enter_enemy_rect(self, char):
        hero_list = []
        hero_list.append(char.get_entity("wizard", (1-char.team_id)))
        hero_list.append(char.get_entity("archer", (1-char.team_id)))

        for hero in hero_list:
            distance = (hero.position - char.position).length()
            if distance < hero.min_target_distance:
                return True
            
        print("False")
        return False
                # def targeted(self, char):


class KnightStateSeeking_TeamA(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight
        
        self.hero_list = ["wizard", "archer"]
        self.knight.path_graph = self.knight.get_lane(self.knight)


    def do_actions(self):

        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # if self.knight.can_heal:
        #     self.knight.heal()
        #     self.knight.can_heal = False
        
        if self.knight.current_hp/self.knight.max_hp < 0.8:
            self.knight.heal()

        if self.knight.colliding(self.knight):
            self.knight.reset(None)
        else:
            #checks if all entities are loaded
            if len(self.knight.world.entities) > 5:
                #checks if knight has a hero to follow, otherwise, check again
                if self.knight.hero == None:
                    print("knight no hero")
                    self.knight.path_graph = self.knight.get_lane(self.knight)
                    self.knight.hero = self.knight.get_entity(self.knight.follow, (1-self.knight.team_id))
                    nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)
                    self.tower = self.knight.get_enemy_tower(self.knight)
                    self.path = pathFindAStar(self.knight.path_graph, \
                                            nearest_node, \
                                            self.knight.path_graph.nodes[self.knight.base.target_node_index])

                    self.path_length = len(self.path)

                    if (self.path_length > 0):
                        self.current_connection = 0
                        self.knight.move_target.position = self.path[0].fromNode.position

                    else:
                        self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position
                    
                    print("Knight in lane", self.knight.paths.index(self.knight.path_graph))
                else:
                    #if hero to follow is alive
                    if not self.knight.hero.ko:
                        print(self.knight.hero.name, " to follow and alive")

                        #hero is alive but not on the same path then move to base respawn and get hero lane
                        if self.knight.hero.world.paths.index(self.knight.hero.path_graph) != self.knight.paths.index(self.knight.path_graph):
                            print(self.knight.hero.name, " not in same lane")
                            self.knight.move_target.position = self.knight.base.spawn_position
                            if (self.knight.position-self.knight.base.spawn_position).length() < 20:
                                print("knight at base")
                                self.knight.path_graph = self.knight.get_lane(self.knight)
                                nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)
                                self.tower = self.knight.get_enemy_tower(self.knight)
                                self.path = pathFindAStar(self.knight.path_graph, \
                                                        nearest_node, \
                                                        self.knight.path_graph.nodes[self.knight.base.target_node_index])

                                self.path_length = len(self.path)

                                if (self.path_length > 0):
                                    self.current_connection = 0
                                    self.knight.move_target.position = self.path[0].fromNode.position

                                else:
                                    self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position
                            print(self.knight.hero.name, " at lane" , self.knight.hero.world.paths.index(self.knight.hero.path_graph))
                            print("knight at lane", self.knight.paths.index(self.knight.path_graph))
                        #hero is alive and on the same path
                        else:
                            print(self.knight.hero.name, " at lane" , self.knight.hero.world.paths.index(self.knight.hero.path_graph))
                            print("knight at lane", self.knight.paths.index(self.knight.path_graph))
                            #check if within 160(hero target distance) of hero, otherwise reposition
                            if(self.knight.position - self.knight.hero.position).length() >= self.knight.hero.min_target_distance:
                                self.knight.move_target.position = self.knight.hero.position
                    
                    # check if opponent is in range
                    nearest_opponent = self.knight.get_nearest_enemy(self.knight)
                    if nearest_opponent is not None:
                        opponent_distance = (self.knight.position - nearest_opponent.position).length()
                        if opponent_distance <= self.knight.min_target_distance:
                            self.knight.target = nearest_opponent
                            return "attacking"
                    
                    if self.knight.position[0] > self.knight.get_enemy_rect(self.knight)[0] and self.knight.position[1] > self.knight.get_enemy_rect(self.knight)[1] and not self.knight.enter_enemy_rect(self.knight):
                        self.knight.velocity = Vector2(0,0)
                    else:
                        if (self.knight.position - self.knight.move_target.position).length() < 8:

                            # continue on path
                            if self.current_connection < self.path_length:
                                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                                self.current_connection += 1
                
            
            
        return None


    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)
        self.tower = self.knight.get_enemy_tower(self.knight)
        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])

        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position

        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


# class KnightStateFollow_TeamA(State):
#     def __init__(self, knight):
#         State.__init__(self, "follow hero")
#         self.knight = knight
#         self.hero = knight.get_entity(self.knight.follow, knight)
#         self.hero_list = ["wizard", "archer"]

#     def do_actions(self):
#         # if wizard is within wizard range, then attract enemies
#         # stay same lane
#         if hasattr(self.hero, "ko"):
#             if not self.hero.ko:
#                 self.knight.velocity = self.knight.move_target.position - self.knight.position
#                 if self.knight.velocity.length() > 0:
#                     self.knight.velocity.normalize_ip();
#                     self.knight.velocity *= self.knight.maxSpeed
#             print("follow_hero")
        
#         else: 
#             return "seeking"
            
#             # self.knight.path_graph = self.knight.get_lane(self.knight)
#         # if self.hero.ko == False:
#         #     if self.knight.follow == "wizard":
#         #         ## if wizard is within wizard range, then attract enemies
#         #     # stay same lane
#         #         self.knight.hero = "wizard"

#         #     elif self.knight.follow == "archer":
#         #         self.knight.hero = "archer"
            
#         #     else:
#         #         return "seeking"

#         return None

#     def check_conditions(self):
#         if self.knight.current_hp/self.knight.max_hp < 0.8:
#             self.knight.heal()

#         if self.knight.colliding(self.knight):
#             self.knight.reset(None)

#         if self.knight.path_graph != self.knight.get_lane(self.knight):
#             self.knight.move_target.position = self.knight.base.position
#         else:
#             if self.knight.position == self.knight.base.spawn_position:
#                 self.knight.path_graph = self.knight.get_lane(self.knight)
#                 return "seeking"

#             if self.hero.ko:
#                 for hero in self.hero_list:
#                     if hero == self.knight.follow:
#                         continue
#                     self.follow = hero
#                     return "seeking"
        
        

#         return None

#     def entry_actions(self):
#         if self.knight.path_graph != self.knight.get_lane(self.knight):
#             self.knight.move_target.position = self.knight.base.position

#         return None


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

        if self.knight.colliding(self.knight):
            self.knight.reset(None)
        
        # else:
        #     if self.knight.current_melee_cooldown/self.knight.melee_cooldown > 0.5:
        #         self.knight.move_back(self.knight)

        # if attacking, while in cooldown and low health
        if self.knight.current_hp/self.knight.max_hp <= 0.2 and self.knight.melee_cooldown > 0:
            self.knight.heal()

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
            self.knight.path_graph = self.knight.get_lane(self.knight)
            return "seeking"
            
        return None

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None
