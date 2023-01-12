import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

from Orc import *

DEBUG2 = False

class Knight_TeamA(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None
        self.targeted = None

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

        Character.render(self, surface)
        if DEBUG2:
            pygame.draw.circle(surface, (0, 0, 0), (int(self.position[0]), int(self.position[1])), int(self.min_target_distance), int(2))

            font = pygame.font.SysFont("arial", 12, True)
            state_name = font.render(self.brain.active_state.name, True, (255, 255, 255))
            surface.blit(state_name, self.position)

            if self.targeted:
                pygame.draw.line(surface, (0, 255, 0), self.position, self.targeted.position)
                pygame.draw.circle(surface, (255, 0, 0), (int(self.position[0]), int(self.position[1])), int(40), int(2))



    def process(self, time_passed):
        
        Character.process(self, time_passed)

        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown"]
        if self.can_level_up():
            choice = randint(0, 100)

            if choice < 30:
                choice = 'hp'
            elif choice < 90:
                choice = 'speed'
            else:
                choice = 'melee damage'

            self.level_up(choice)     

    def get_nearest_tower(self, char):

        nearest_tower = None
        distance = 0.

        for entity in self.world.entities.values():

            if entity.team_id == 2:
                continue

            if entity.team_id == char.team_id:
                continue

            if entity.name == "projectile" or entity.name == "explosion" or entity.name == "knight" or entity.name == "archer" or entity.name =="wizard" or entity.name == "orc":
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
                        orc_lane[str(i)] += enemy_orc.melee_damage

            if entity.name == 'knight' or entity.name == 'archer' or entity.name == 'wizard':
                enemy = entity
                enemy_path2 = enemy.brain.states['seeking'].path
                for i in range(0, len(self.world.paths)):
                    if enemy_path2 == self.world.paths[i]:
                        orc_lane[str(i)] += enemy.melee_damage
            
            if entity.name == 'tower' and entity.ko == True:
                # print("tower dead")
                lane_with_least == self.world.paths[0]
                return lane_with_least
    
        for key in orc_lane.keys():
            if orc_lane[key] == min(orc_lane.values()):
                lane_with_least = self.world.paths[int(key)]
                # print("lane_values", orc_lane.values(), "key", key)
            continue

        # print("lane 3", lane_with_least)
        return lane_with_least
    
    def get_targeted(self, char):
        for entity in self.world.entities.values():
            if entity.team_id == char.team_id or entity.team_id == 2:
                continue

            if entity.name == 'orc' or entity.name == 'knight':
                if entity.target == char:
                    self.targeted = entity

            if entity.name == 'projectile' or entity.name == 'explosion':
                if entity.owner.target == char:
                    self.targeted = entity 

        # print(self.targeted)
    def dodge_attack(self, char):
        if char.targeted:
            if(char.position - char.targeted.position).length() < 10:
                # print("dodged")
                if char.position[0] < char.targeted.position[0] and char.position[1] > char.targeted.position[1]:
                    char.position[0] += 20
                if char.position[0] > char.targeted.position[0] and char.position[1] < char.targeted.position[1]:
                    char.position[1] += 20
                if char.position[0] == char.targeted.position[0] and char.position[1] < char.targeted.position[1]:
                    char.position[0] += 20
                if char.position[0] < char.targeted.position[0] and char.position[1] == char.targeted.position[1]:
                    char.position[1] += 20
                if char.position[0] > char.targeted.position[0] and char.position[1] > char.targeted.position[1]:
                    char.position[0] += 20
                if char.position[0] < char.targeted.position[0] and char.position[1] > char.targeted.position[1]:
                    char.position[0] += 20
                if char.position[0] == char.targeted.position[0] and char.position[1] > char.targeted.position[1]:
                    char.position[0] += 20
                if char.position[0] > char.targeted.position[0] and char.position[1] == char.targeted.position[1]:
                    char.position[1] += 20
                # char.targeted.position[randint(0,1)] += 20



class KnightStateSeeking_TeamA(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight
        # print("instantiate")
        self.knight.path_graph = self.knight.get_least_lane(self.knight)


    def do_actions(self):

        self.knight.get_targeted(self.knight)
        self.knight.dodge_attack(self.knight)
        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):
        # # check if opponent is in range
        # self.knight.get_targeted(self.knight)
        self.knight.path_graph = self.knight.get_least_lane(self.knight)
        nearest_opponent = self.knight.get_nearest_tower(self.knight)

        if nearest_opponent is not None:
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                    self.knight.target = nearest_opponent
                    self.knight.targeted = None
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
        # self.knight.get_targeted(self.knight)
        # self.knight.dodge_attack(self.knight)
        self.knight.targeted = None
        if pygame.sprite.collide_rect(self.knight, self.knight.target) and self.knight.targeted == None:
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
            # self.knight.path_graph = self.knight.world.paths[randint(0, len(self.knight.world.paths)-1)]
            self.knight.path_graph =   self.knight.get_least_lane(self.knight)
            self.knight.targeted = None
            return "seeking"
            
        return None

    def entry_actions(self):
        # print("dead")

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None
        self.knight.targeted = None

        return None
