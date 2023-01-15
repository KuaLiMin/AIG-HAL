import pygame

from random import randint, random
from Graph import *

import math

from Character import *
from State import *

MYDEBUG = False

MOVETARGETDEBUG = False

class Wizard_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100


        

        seeking_state = WizardStateSeeking_TeamA(self)
        attacking_state = WizardStateAttacking_TeamA(self)
        ko_state = WizardStateKO_TeamA(self)
        returning_state = WizardStateReturning_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(returning_state)

        self.brain.set_state("seeking")

       
        self.text = ""

    def render(self, surface):

        if MOVETARGETDEBUG:
            # if self.move_target is set, blit pink dot
            if self.move_target is not None:
                pygame.draw.circle(surface, (255, 0, 255), (int(self.move_target.position[0]), int(self.move_target.position[1])), 10)


        
        if MYDEBUG:
            widthbuffer = SCREEN_WIDTH/11
            heightbuffer = SCREEN_WIDTH/11

            # draw line heightbuffer pixels from the top and bottom of screen
            pygame.draw.line(surface, (0, 0, 0), (0, heightbuffer), (SCREEN_WIDTH, heightbuffer), 1)
            pygame.draw.line(surface, (0, 0, 0), (0, SCREEN_HEIGHT - heightbuffer), (SCREEN_WIDTH,  SCREEN_HEIGHT - heightbuffer), 1)
            pygame.draw.line(surface, (0, 0, 0), (heightbuffer, 0), (heightbuffer, SCREEN_HEIGHT), 1)
            pygame.draw.line(surface, (0, 0, 0), (SCREEN_WIDTH - heightbuffer, 0), (SCREEN_WIDTH - heightbuffer,  SCREEN_HEIGHT), 1)
            
            path1polygon = [(0, 255), (165, 244), (247, 571), (325, 639), (736, 634), (755, 758), (0, 756)]
            path0polygon = [(313, 143), (300, 0), (1024, 0), (1024, 470), (870, 480),(798, 171)]
            # blit both polygons
            pygame.draw.polygon(surface, (0, 0, 0), path1polygon, 1)
            pygame.draw.polygon(surface, (0, 0, 0), path0polygon, 1)

            # draw circle around target
            if self.target is not None:
                target = self.target

                radius = 140
                distance_between_dots = 25
                circumference = 2 * math.pi * radius 
                num_dots = int(circumference / distance_between_dots)

                # Create a list to store the dot coordinates
                dot_list = []

                # Calculate the angle between each dot
                angle = 360 / num_dots

                # Create a loop to calculate the coordinates of each dot
                for i in range(num_dots):
                    # Add the dot coordinates to the list
                    dot_list.append((target.position[0] + radius * math.cos(math.radians(i * angle)), target.position[1] + radius * math.sin(math.radians(i * angle))))

                # Draw the dots
                for dot in dot_list:
                    pygame.draw.circle(surface, (0, 0, 0), dot, 5)      



            # draw world paths
            # for connection in self.world.paths[1].connections:
            #     pygame.draw.line(surface, (0, 0, 0), (int(connection.fromNode.position[0]), int(connection.fromNode.position[1])), (int(connection.toNode.position[0]), int(connection.toNode.position[1])), 1)

            # draw world paths
            # for connection in self.world.paths[0



            # draw circle around target
            if self.target is not None:
                target = self.target

                radius = 140


            if self.target is not None:
                target = self.target

                radius = 140 # circle around target
                distance_between_dots = 20
                circumference = 2 * math.pi * radius 
                num_dots = int(circumference / distance_between_dots)

                # Create a list to store the dot coordinates
                dot_list = []

                # Calculate the angle between each dot
                angle = 360 / num_dots

                # Create a loop to calculate the coordinates of each dot
                for i in range(num_dots):
                    # Add the dot coordinates to the list
                    dot_list.append((target.position[0] + radius * math.cos(math.radians(i * angle)), target.position[1] + radius * math.sin(math.radians(i * angle))))

                # Draw the dots
                for dot in dot_list:
                    pygame.draw.circle(surface, (0, 0, 0), dot, 5)      

                # if self.move_target is set, blit pink dot
                if self.move_target is not None:
                    pygame.draw.circle(surface, (255, 0, 255), (int(self.move_target.position[0]), int(self.move_target.position[1])), 10)
 

            # draw world paths
            # for connection in self.world.paths[1].connections:
            #     pygame.draw.line(surface, (0, 0, 0), (int(connection.fromNode.position[0]), int(connection.fromNode.position[1])), (int(connection.toNode.position[0]), int(connection.toNode.position[1])), 5)

            # # blit circle at target
            # if self.target is not None:
            #     pygame.draw.circle(surface, (255, 100, 0), (int(self.target.position[0]), int(self.target.position[1])), 40, 20)
            #     pygame.draw.circle(surface, (255, 0, 100), (int(self.target.position[0]), int(self.target.position[1])), 50, 10)


            # if towerisok
            if self.towerIsOk():
                # blit circle around base
                pygame.draw.circle(surface, (0, 255, 0), (int(self.base.position[0]), int(self.base.position[1])), 100, 10)
            else:
                # blit circle around base
                pygame.draw.circle(surface, (255, 0, 0), (int(self.base.position[0]), int(self.base.position[1])), 100, 10)

            # blit indicator around entities near base
            for i in self.world.entities:
                entity = self.world.entities[i]

                if self.isNonLiving(entity):
                    continue
                #if entity is self
                if entity != self:
                    # if entity is opponent
                    if entity.team_id == self.team_id:
                        continue
                
                # if entity is near base
                if self.near_base(entity,3.75):
                    # draw square around entity
                    entity.radius = 20
                    pygame.draw.rect(surface, (255, 100, 0), (int(entity.position[0]-entity.radius), int(entity.position[1]-entity.radius), int(entity.radius*2), int(entity.radius*2)), 2)
                elif self.near_base(entity,3):
                    # draw square around entity
                    entity.radius = 20
                    pygame.draw.rect(surface, (200, 255, 0), (int(entity.position[0]-entity.radius), int(entity.position[1]-entity.radius), int(entity.radius*2), int(entity.radius*2)), 2)
                elif self.near_base(entity,2.5):
                    # draw square around entity
                    entity.radius = 20
                    pygame.draw.rect(surface, (60, 255, 50), (int(entity.position[0]-entity.radius), int(entity.position[1]-entity.radius), int(entity.radius*2), int(entity.radius*2)), 2)
                elif self.near_base(entity,2.4):
                    # draw square around entity
                    entity.radius = 20
                    pygame.draw.rect(surface, (60, 60, 200), (int(entity.position[0]-entity.radius), int(entity.position[1]-entity.radius), int(entity.radius*2), int(entity.radius*2)), 2)


            # blit indicator around strongest entity
            if self.near_base_opponent_count(1) > 0:
                strongestentity= self.near_base_strongest_opponent()
                if strongestentity is not None:
                    strongestentity.radius = 30
                    pygame.draw.rect(surface, (255, 0, 0), (int(strongestentity.position[0]-strongestentity.radius), int(strongestentity.position[1]-strongestentity.radius), int(strongestentity.radius*2), int(strongestentity.radius*2)), 5)


            # blit text above every opponent entity
            for i in self.world.entities:
                entity = self.world.entities[i]

                if self.isNonLiving(entity):
                    continue
                
                #if entity is self
                if entity != self:
                    if entity.team_id == self.team_id:
                        continue

                # blit current hp above entity
                font = pygame.font.SysFont("monospace", 15, True)
                state_name = font.render(str((round(self.entitydamage(entity),0))) + "  "+ str(self.entity_path_index(entity)), True, (200, 255, 200))
                surface.blit(state_name, (int(entity.position[0]-30), int(entity.position[1]-30)))

            # if self.wizard.dot_list exists
            if hasattr(self, 'dot_list'):
                coor = self.dot_list

                # draw circle around coorindates
                for i in range(int((len(coor)))):
                     pygame.draw.circle(surface, (100, 100, 255), (coor[i][0], coor[i][1]),  (i/2)+4)

                     # blit index on circle
                     state_name = pygame.font.SysFont("monospace", 15, True).render(str(i), True, (200, 255, 200))
                     surface.blit(state_name, (int(coor[i][0]-10), int(coor[i][1]-10)))
                

            if hasattr(self, 'dot_list'):
                print("oo")



            # mark path in list of coordinates and clostest node
            
            if hasattr(self, "path_graph") and self.brain.active_state.name != "ko":
                # draw circle around coorindates
                pygame.draw.circle(surface, (100, 100, 255), self.path_graph.nodes[self.base.spawn_node_index].position, 20)

                pygame.draw.circle(surface, (255, 100, 255), self.path_graph.get_nearest_node(self.position).position, 15)

                # draw the nodes
                for nodeKey in self.path_graph.nodes:
                    pygame.draw.circle(surface, (180, 90, 180), self.path_graph.nodes[nodeKey].position, 10)
                    surface.blit(pygame.font.SysFont("arial", 15, True).render(str((self.path_graph.nodes[nodeKey].position[0]-20, (self.path_graph.nodes[nodeKey].position[1]-20))), 1, (255, 220, 255)), (self.path_graph.nodes[nodeKey].position[0]-20, (self.path_graph.nodes[nodeKey].position[1]-20)))





                    
        
               # pygame.draw.polygon(surface, (255, 0, 100), ((int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[0]), int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[1])), (int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[0]-10), int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[1]+10)), (int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[0]+10), int(self.path_graph.nodes[len(self.path_graph.nodes)-1].position[1]+10))), 0)

            # trace path in graph object


        Character.render(self, surface)


    def process(self, time_passed):


        #update node property

        # if object has property
        
        if MYDEBUG:

            if hasattr(self, "path"):
                if (self.current_connection < len(self.path)):
                    self.text = self.brain.active_state.name
                else:
                    self.text = self.brain.active_state.name
            else:

                self.text = self.brain.active_state.name
            
            self.text += " " + str(self.entity_path_index(self))
            

        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        if self.can_level_up():
            # random number between 0 and 100

            choice = randint(0, 100)

            if choice < 20:
                choice = 'hp'
            elif choice < 80:
                choice = 'speed'
            elif choice < 90:
                choice = 'ranged cooldown'
            else:
                choice = 'ranged damage'

            self.level_up(choice)      

    def point_in_polygon(self,point, polygon):
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x < max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    # get entity damage
    def entitydamage(self, entity):
        if hasattr(entity, "melee_damage"):
            if hasattr(entity, "ranged_damage"):
                if entity.melee_damage > entity.ranged_damage:
                    return entity.melee_damage
                else:
                    return entity.ranged_damage
            else:
                return entity.melee_damage
        else:
            return entity.ranged_damage


    # function to find index of path list that entity belongs in
    def entity_path_index(self, entity):
        buffer = SCREEN_WIDTH/11

        
        # polygons to counter irregular shapes
        path1polygon = [(0, 255), (165, 244), (247, 571), (325, 639), (736, 634), (755, 758), (0, 756)]
        path0polygon = [(313, 143), (300, 0), (1024, 0), (1024, 470), (870, 480),(798, 171)]

        if self.point_in_polygon(entity.position, path1polygon):
            return 1
        elif self.point_in_polygon(entity.position, path0polygon):
            return 0

        near_top = entity.position[1] <= buffer
        near_bottom = entity.position[1] >= SCREEN_HEIGHT - buffer
        near_left = entity.position[0] <= buffer
        near_right = entity.position[0] >= SCREEN_WIDTH - buffer

        # if entity is within buffer distance of any screen edge
        # return relavant path index

        # --------------
        # |          0 |
        # | 1          |
        # --------------


        # if enttty is near top or right, but not near bottom and left
        if (near_top or near_right) and not (near_bottom or near_left):
            return 0

        # if entity is near bottom or left, but not near top and right
        if (near_bottom or near_left) and not (near_top or near_right):
            return 1





        # else find nearest node and return path index

        closest_distance = 1000000
        path_index = 0
        for i in range(2, len(self.world.paths)):
            distance = (Vector2(entity.position) - Vector2(self.world.paths[i].get_nearest_node(entity.position).position)).length()
            if distance < closest_distance:
                closest_distance = distance
                path_index = i
            

        return path_index


    # get path most neglected by team
    def neglected_path_index(self):
        # create dictionary of path indexes and number of entities in each path
        path_dict = {}

        # loop indexes of list
        for i in range(0, len(self.world.paths)):
            path_dict[i] = 0






        # for each hero/orc from same team in world
        for i in self.world.entities:
            entity = self.world.entities[i]

            multiplier = 1

            if self.isNonLiving(entity):
                continue

            if entity.team_id != self.team_id:
                multiplier = -1
                

            # get path index of entity
            path_index = self.entity_path_index(entity)


            # if path index is in dictionary
            if path_index in path_dict:
                # increment value
                path_dict[path_index] += self.entitydamage(entity) * multiplier
            else:
                # add path index to dictionary
                path_dict[path_index] += self.entitydamage(entity) * multiplier

        if MYDEBUG:
            print("path dict") 
            for key in path_dict:
                print(key, path_dict[key]) 

        if path_dict == {}: # if no paths in dictionary
            # randomly choose between 2 and 3
            return randint(2, 3)

        else:
            # find path index with lowest value
            lowest_value = 1000000
            for i in path_dict:
                if path_dict[i] < lowest_value:
                    lowest_value = path_dict[i]

            
            # if multiple paths have lowest_value, choose one at semi-random
            lowest_indexes = []
            for i in path_dict:
                if path_dict[i] == lowest_value:
                    lowest_indexes.append(i)
                    # if index is 2 or 3, add two more times to increase chance of choosing
                    #                                            (since they are the shortest paths)
                    if i == 2 or i == 3:
                        lowest_indexes += ([i] * 2)
            
            # choose random path index from lowest_indexes
            return lowest_indexes[randint(0, len(lowest_indexes) - 1)]


    def get_nearest_living_opponent(self):

        nearest_opponent = None
        distance = 0.

        for entity in self.world.entities.values():

            # neutral entity
            if entity.team_id == 2:
                continue

            # same team
            if entity.team_id == self.team_id:
                continue

            if self.isNonLiving(entity):
                continue

            if entity.ko:
                continue

            if nearest_opponent is None:
                nearest_opponent = entity
                distance = (self.position - entity.position).length()
            else:
                if distance > (self.position - entity.position).length():
                    distance = (self.position - entity.position).length()
                    nearest_opponent = entity
        
        return nearest_opponent


    # if entity is near base
    def near_base(self, entity, portion):
        if ((entity.position[0] - self.base.position[0])**2 + (entity.position[1] - self.base.position[1])**2 < (SCREEN_WIDTH / portion)**2) :
            return True
        return False

    # if entity is not a hero or orc
    def isNonLiving(self, entity):
        # neutral entity
        if entity.team_id == 2:
            return True

        if entity.name == "projectile" or entity.name == "explosion" or entity.name == "base" or entity.name == "tower":
            return True
        if entity.ko:
            return True
        return False

    # count of opponents near base for range
    def near_base_opponent_count(self, portion):
        count = 0
        # for all entities
        for i in self.world.entities:
            entity = self.world.entities[i]

            if self.isNonLiving(entity):
                continue

            # if entity is opponent
            if entity.team_id == self.team_id:
                continue
            
            # if entity is near base
            if self.near_base(entity,portion):
                count += 1

        return count

    # strongest opponent near base
    def near_base_strongest_opponent(self):
        strongest = None
        # for all entities
        for i in self.world.entities:
            entity = self.world.entities[i]

            if self.isNonLiving(entity):
                continue

            # if entity is opponent
            if entity.team_id == self.team_id:
                continue
            
           

            # if entity is near base
            if self.near_base(entity,3):
                if strongest == None:
                    strongest = entity
                else:
                    if self.entitydamage(entity) > self.entitydamage(strongest):
                        strongest = entity
                

        if strongest == None:
            strongest = self.get_nearest_living_opponent()

        return strongest


    # total hp of enemies in two fifths screen width of entityA
    def opponentDamage_in_range(self, entityA):
        total_dam = 0
        for i in self.world.entities:

            entity = self.world.entities[i]
            if self.isNonLiving(entity):
                continue
                
            if entity.team_id == self.team_id:
                continue            

            if self.near_base(entity,2.5):
                total_dam += self.entitydamage(entity)

        return total_dam

    # If situation with towers is ok 
    def towerIsOk(self):

        # count of opponents within 2.5 range around base
        oppCount = self.near_base_opponent_count(2.5)

        # it is immediately ok if there are no opponents, no need to check towers
        if oppCount == 0:
            return True      

        # it is immediately not ok if there are opponents within smaller 3.75 range around base
        if self.near_base_opponent_count(3.75) > 0: 
            return False


        # checking towers, ok means:
        # - there are two towers on team
        #  AND
        # - average damage * three hits is less than average hp of towers

        towerCount = 0
        tower_HP = 0

        # check for towers on team
        for i in self.world.entities:
            entity = self.world.entities[i]
            if entity.name == "tower":
                if entity.team_id == self.team_id:
                    towerCount += 1
                    tower_HP += entity.current_hp

        if towerCount > 0:
        
            oppDamage = self.opponentDamage_in_range(self.base)
            if towerCount == 2 and (oppDamage/oppCount * 3) < tower_HP/towerCount: 
                return True
            
        return False




class WizardStateSeeking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
        

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

    def check_conditions(self):

        # if timer  seconds or less in
        if self.wizard.world.countdown_timer >= TIME_LIMIT - 1:
            return "seeking"


        # calculate what "close enough" means based on path
        closeEnoughRange = 2.5 # by default
        # since path 1 and 0 are longer, give them bigger range portion
        path_index = self.wizard.entity_path_index
        if path_index == 1 or path_index == 0:
            closeEnoughRange = 2.4


        # if wizard is close enough (but not already at base) and towers are struggling, make wizard go back
        if not(self.wizard.near_base(self.wizard, 5.3)) and self.wizard.near_base(self.wizard,closeEnoughRange) and not(self.wizard.towerIsOk()):

            print("|| SEEKING > RETURNING") if MYDEBUG else None
            return "returning"


        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if opponent_distance <= self.wizard.min_target_distance:
                    self.wizard.target = nearest_opponent
                    print("|| SEEKING > ATTACKING") if MYDEBUG else None
                    return "attacking"
        
        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None
        

    def entry_actions(self):
        
        # SET NEW PATH GRAPH IF NEAR BASE

        path_index = 0

        if self.wizard.near_base(self.wizard,3.75):

            if self.wizard.world.countdown_timer<= TIME_LIMIT/2.5:
                print("            TIME IS RUNNING OUT")
            if self.wizard.base.current_hp <= self.wizard.base.current_hp/3.5:
                print("            LOW HEALTH")

            # if tower is ok
            if self.wizard.towerIsOk() or (self.wizard.world.countdown_timer<= TIME_LIMIT/2.5 and self.wizard.base.current_hp > self.wizard.base.current_hp/3.5):



                path_index = self.wizard.neglected_path_index()
                print("SEEKING | NEGLECTED PATH", end=" | ") if MYDEBUG else None

            # if tower is not ok (opponents are near base + buildings might not be able to handle)
            else:
                # pick path of strongest nearby opponent
                path_index = self.wizard.entity_path_index(self.wizard.near_base_strongest_opponent())
                print("SEEKING | STRONGEST NEARBY PATH", end=" | ") if MYDEBUG else None

            print(path_index)  if MYDEBUG else None

            # set path to new path

            self.wizard.path_graph = self.wizard.world.paths[path_index]

            nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

            self.path = pathFindAStar(self.wizard.path_graph, \
                                nearest_node, \
                                self.wizard.world.paths[path_index].nodes[self.wizard.base.target_node_index])

            
        # not near base, continue with current path
        else:
            self.wizard.path_graph = self.wizard.world.paths[self.wizard.entity_path_index(self.wizard)]
    
            nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)
            self.path = pathFindAStar(self.wizard.path_graph, \
                               nearest_node, \
                               self.wizard.path_graph.nodes[self.wizard.base.target_node_index])

            print("SEEKING | CONTINUE TO OPPOSING BASE") if MYDEBUG else None

        

        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position

        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index].position




class WizardStateReturning_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "returning")
        self.wizard = wizard
        

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

    def check_conditions(self):
        if (self.wizard.near_base(self.wizard,3.8) or self.wizard.towerIsOk()) or (self.wizard.near_base(self.wizard,3.75)):
            nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
            if nearest_opponent is not None:
                opponent_distance = (self.wizard.position - nearest_opponent.position).length()
                if opponent_distance <= self.wizard.min_target_distance:
                        self.wizard.target = nearest_opponent
                        print("|| RETURNING > ATTACKING") if MYDEBUG else None
                        return "attacking"

            print("|| RETURNING > SEEKING") if MYDEBUG else None
            return "seeking"





        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
        

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)
        self.path = pathFindAStar(self.wizard.path_graph, \
                            nearest_node, \
                            self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index])

        print("RETURN | GO BACK TO BASE | ",  end="") if MYDEBUG else None


        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position
            print() if MYDEBUG else None
        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index].position
        
        return None








class WizardStateAttacking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard
        self.dot_list = []
        self.dotIndex = 0
        self.multiplier = 1
        self.collisionCount = 0
        self.collision = False

    def do_actions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        # if nearest opponent is builidng, set to that
        if self.wizard.world.get_nearest_opponent(self.wizard) == "base" or  self.wizard.world.get_nearest_opponent(self.wizard) == "tower":
            self.wizard.target = self.wizard.world.get_nearest_opponent(self.wizard)

        # opponent within range, attack. if not, move towards opponent.
        if opponent_distance <= self.wizard.min_target_distance:
            self.wizard.velocity = Vector2(0, 0)
            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)

        else:
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed


    def check_conditions(self):
        

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            return "seeking"

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        if opponent_distance > (1.5 * self.wizard.min_target_distance):
            self.wizard.target = None
            return "seeking"


        # see if entity is colliding
        collision_list = pygame.sprite.spritecollide(self.wizard, self.wizard.world.obstacles, False, pygame.sprite.collide_mask)
        self.collision = False
        for entity in collision_list:
            if entity.name == "obstacle" or entity.name == "base"  or entity.name == "tower":
                self.collision = True
                self.collisionCount += 1
                print("hit base or tower") if MYDEBUG else None
                break

        



      
        # if move target reached
        if (self.wizard.position - self.wizard.move_target.position).length() < 8 or self.collision:
            if self.collision and ((self.wizard.position - self.wizard.move_target.position).length() < 8):
                
                print('exit collision')  if MYDEBUG else None
                self.collision = False
                self.collisionCount = 0




            
            if self.dotIndex + 1 == len(self.dot_list) or self.dotIndex == 0 or self.collisionCount == 1:
                # change multiplier
                self.multiplier = -self.multiplier

            if self.dotIndex <= self.dotCount:

                new_target = self.dot_list[self.dotIndex]

                self.wizard.move_target.position = self.dot_list[self.dotIndex]
                self.dotIndex+=self.multiplier
        else:
            self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed


        # if colliding for too long
        if self.collisionCount > 300:
            self.wizard.path_graph = self.wizard.world.paths[self.wizard.entity_path_index(self.wizard)]
            nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

            self.wizard.move_target.position = nearest_node.position

            if self.collisionCount > 600:
                self.collisionCount = 0
                self.collision = False
                self.wizard.target = None
                return "seeking"
            return "seeking"

        
        print("INDEX", "                              ", self.dotIndex, self.dotCount, self.collisionCount) if MYDEBUG else None

        return None
            




    def entry_actions(self):
        target = self.wizard.target
        radius = self.wizard.min_target_distance -20

        if self.wizard.near_base(self.wizard, 5):
            radius = self.wizard.min_target_distance - 20
        
        
        # circle around target - 10 just in case
        # if not(self.wizard.target.name == "orc" or self.wizard.target.name == "knight"):
        #     if (self.wizard.min_target_distance < self.wizard.target.min_target_distance):
        #         radius = (self.wizard.target.min_target_distance + self.wizard.min_target_distance)/2
            

       
        distance_between_dots = 20
        circumference = 2 * math.pi * radius 
        num_dots = int(circumference / distance_between_dots)

        # Create a list to store the dot coordinates
        self.dot_list = []

        # Calculate the angle between each dot
        angle = 360 / num_dots


        first_dot_index = 0
        onScreenList = []
        isPastFirstOffscreen = False

        # Create a loop to calculate the coordinates of each dot
        for i in range(num_dots):
            # Add the dot coordinates to the list
            # if dot is not off screen

            x = target.position[0] + radius * math.cos(math.radians(i * angle))
            y = target.position[1] + radius * math.sin(math.radians(i * angle))

            # if on screen and first off screen has passed
            if isPastFirstOffscreen and (x > 3 and x < SCREEN_WIDTH -3 and y > 3 and y < SCREEN_HEIGHT -3):
                first_dot_index = i
                break
            
            # if off screen
            if not(x > 3 and x < SCREEN_WIDTH -3 and y > 3 and y < SCREEN_HEIGHT -3):
                isPastFirstOffscreen = True
        


        # Create a loop to calculate the coordinates of each dot
        for i in range(num_dots):
            # Add the dot coordinates to the list

            x = target.position[0] + radius * math.cos(math.radians(i * angle))
            y = target.position[1] + radius * math.sin(math.radians(i * angle))
            onScreenList.append((x,y))

           
        # change self.dot list to start at first dot index
        onScreenList = onScreenList[first_dot_index:] + onScreenList[:first_dot_index]

        # remove off screen dots
        for i in onScreenList:
            
           
            if i[0] > 3 and i[0] < SCREEN_WIDTH -3 and i[1] > 3 and i[1] < SCREEN_HEIGHT -3:
                
                # append to self.dot_list
                self.dot_list.append(i)

                

        # if last dot is closer than first dot, reverse the list
        if (self.dot_list[0] - self.wizard.position).length() > (self.dot_list[len(self.dot_list) -1] - self.wizard.position).length():
            # reverse list
            self.dot_list = self.dot_list[::-1]

            

        
     
        # find closest dot index in dot index list
        closest_dot_index = 0
        closest_distance = 1000000
        for i in range(len(self.dot_list)):
            distance = (self.wizard.position - self.dot_list[i]).length()
            if distance < closest_distance:
                closest_distance = distance
                closest_dot_index = i

        
    
        self.collisionCount = 0
        self.dotCount = len(self.dot_list)



        # print self.dot_list with index
        for i in range(len(self.dot_list)):
            print(i, "   ", self.dot_list[i]) if MYDEBUG else None

        self.wizard.dot_list = self.dot_list


        if (self.dotCount > 0):
            self.dotIndex = closest_dot_index
            self.multiplier = 1
            self.wizard.move_target.position = self.dot_list[closest_dot_index]
            print() if MYDEBUG else None
        else:
            self.wizard.move_target.position = self.wizard.position
        
        return None















class WizardStateKO_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "ko")
        self.wizard = wizard

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.wizard.current_respawn_time <= 0:
            self.wizard.current_respawn_time = self.wizard.respawn_time
            self.wizard.ko = False
            # self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
            
            print("|| KO > SEEKING") if MYDEBUG else None
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None
