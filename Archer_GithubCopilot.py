import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Archer_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = ArcherStateSeeking_TeamA(self)
        attacking_state = ArcherStateAttacking_TeamA(self)
        ko_state = ArcherStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        if self.can_level_up():
            choice = randint(0, len(level_up_stats) - 1)
            self.level_up(level_up_stats[choice])   


class ArcherStateSeeking_TeamA(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]


    def do_actions(self):

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"
    
        if (self.archer.position - self.archer.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
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

    def do_actions(self):

        # Update nearest opponent if new one overtakes old one
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if (self.archer.position - nearest_opponent.position).length() <= self.archer.min_target_distance:
            self.archer.target = nearest_opponent

        opponent_distance = (self.archer.position - self.archer.target.position).length()

        # opponent within range
        if opponent_distance <= self.archer.min_target_distance:
            self.archer.velocity = Vector2(0, 0)
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)
                return "seeking"

        else:
            self.archer.velocity = self.archer.target.position - self.archer.position
            if self.archer.velocity.length() > 0:
                self.archer.velocity.normalize_ip();
                self.archer.velocity *= self.archer.maxSpeed

        #move back while attacking enemy (if it is an orc or knight)
        if (self.archer.target.name == "orc" or self.archer.target.name == "knight") and opponent_distance <= self.archer.min_target_distance - 30:
            if self.curr_conn < len(self.path):
                self.archer.velocity = self.path[self.curr_conn].toNode.position - self.archer.position
                if (self.archer.position - self.path[self.curr_conn].toNode.position).length() < 8:
                    self.curr_conn += 1
            else:
                self.archer.velocity = self.archer.position - self.archer.target.position
            self.archer.velocity.normalize_ip()
            self.archer.velocity *= self.archer.maxSpeed
            # self.archer.velocity = self.archer.position - self.archer.target.position
            # if self.reached_boundary():
            #     for entity in self.archer.world.entities.values():
            #         if entity.team_id == self.archer.team_id and entity.name == "base":
            #             self.archer.velocity = entity.position - self.archer.position
            # self.archer.velocity.normalize_ip();
            # self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"

        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)
        self.path = pathFindAStar(self.archer.path_graph, \
                                nearest_node, \
                                self.archer.path_graph.nodes[self.archer.base.spawn_node_index])

        self.path_length = len(self.path)
        self.curr_conn = 0
            
        return None

    def reached_boundary(self):

        #Check if edge of screen
        if self.archer.position[0] - 10 <= 0 or self.archer.position[0] + 10 >= SCREEN_WIDTH or\
            self.archer.position[1] - 10 <= 0 or self.archer.position[1] +10 >= SCREEN_HEIGHT:
            return self.archer.position
        
        #Check if touches base or obstacle
        collision_list = pygame.sprite.spritecollide(self.archer, self.archer.world.obstacles, False, pygame.sprite.collide_mask)
        for entity in collision_list:
            if entity.name == "obstacle" or entity.name == "base":
                return entity.position
        
        return False



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
            self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None
