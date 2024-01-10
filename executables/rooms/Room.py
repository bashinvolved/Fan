import random

import pygame.sprite

from executables.entities.Belle import Belle
from executables.rooms.obstacles.Fridge import Fridge
from executables.entities.Catterfield import Catterfield


class Room:
    def __init__(self, r):
        self.r = r
        self.image = self.r.drawable("tiles")
        self.obstacles_group = pygame.sprite.Group()
        self.max_count_of_obstacles = 5
        self.max_count_of_enemies = 4
        self.entities_group = pygame.sprite.Group()
        self.build()
        self.populate()

    def populate(self):
        self.entities_group.empty()
        for i in range(random.randrange(1, self.max_count_of_enemies)):
            next_enemy = (choiced := random.choice((Catterfield, )))(self.r, f"{choiced.__name__.lower()}_movement",
                                                                     200)
            x, y = (random.randrange(self.image.get_rect().width - next_enemy.rect.width),
                    random.randrange(self.image.get_rect().height - next_enemy.rect.height))
            next_enemy.rect.x, next_enemy.rect.y = x, y
            while pygame.sprite.spritecollideany(next_enemy, self.obstacles_group) or \
                    pygame.sprite.spritecollideany(next_enemy, self.entities_group):
                x, y = (random.randrange(self.image.get_rect().width - next_enemy.rect.width),
                        random.randrange(self.image.get_rect().height - next_enemy.rect.height))
                next_enemy.rect.x, next_enemy.rect.y = x, y
            next_enemy.x = next_enemy.rect.x
            next_enemy.y = next_enemy.rect.y
            self.add_entity(next_enemy)

    def build(self):
        self.obstacles_group.empty()
        for i in range(random.randrange(1, self.max_count_of_obstacles)):
            next_obstacle = random.choice((Fridge, ))(self.r)
            x, y = (random.randrange(self.image.get_rect().width - next_obstacle.rect.width),
                    random.randrange(self.image.get_rect().height - next_obstacle.rect.height))
            next_obstacle.rect.x, next_obstacle.rect.y = x, y
            while pygame.sprite.spritecollideany(next_obstacle, self.obstacles_group) or \
                    pygame.sprite.spritecollideany(next_obstacle, self.entities_group):
                x, y = (random.randrange(self.image.get_rect().width - next_obstacle.rect.width),
                        random.randrange(self.image.get_rect().height - next_obstacle.rect.height))
                next_obstacle.rect.x, next_obstacle.rect.y = x, y
            self.obstacles_group.add(next_obstacle)

    def add_entity(self, entity):
        self.entities_group.add(entity)

    def draw_obstacles(self, surface):
        for obstacle in self.obstacles_group.sprites():
            surface.blit(obstacle.image, (obstacle.rect.x, obstacle.rect.y))

    def draw_entities(self, surface, hand_mode=False):
        for entity in self.entities_group.sprites() if not hand_mode else (self.find_belle(),):
            if isinstance(entity, Belle) and not hand_mode:
                continue
            x = min(self.image.get_rect().width - entity.rect.width, max(0, entity.rect.x))
            y = min(self.image.get_rect().height - entity.rect.height, max(0, entity.rect.y))
            if entity.rect.x != x:
                entity.undo_move_x()
            if entity.rect.y != y:
                entity.undo_move_y()
            surface.blit(entity.image, (entity.rect.x, entity.rect.y))

    def draw_belle(self, surface):
        entity = self.find_belle()
        if pygame.sprite.spritecollideany(entity, self.obstacles_group):
            entity.undo_move_x()
            if pygame.sprite.spritecollideany(entity, self.obstacles_group):
                entity.redo_move_x()
                entity.undo_move_y()
                if pygame.sprite.spritecollideany(entity, self.obstacles_group):
                    entity.undo_move_x()
                    entity.undo_move_y()
        self.draw_entities(surface, True)

    def draw_bullets(self, surface):
        iteration_bin = self.find_belle().weapons[0].bullets_group.sprites()
        for bullet in iteration_bin:
            for enemy in filter(lambda elem: not isinstance(elem, Belle), self.entities_group.sprites()):
                if pygame.sprite.collide_rect(bullet, enemy):
                    enemy.add_damaging_bullet(bullet)
            bullet.draw(surface)

    def find_belle(self):
        try:
            return next(filter(lambda elem: isinstance(elem, Belle), self.entities_group.sprites()))
        except StopIteration:
            pass

    def draw_weapon(self, surface):
        surface.blit((we := self.find_belle().weapons[0]).image, we.rect[:2])

    def draw(self):
        this_room = pygame.Surface((self.image.get_rect().width, self.image.get_rect().height))
        this_room.blit(self.image, (0, 0))
        self.draw_obstacles(this_room)
        self.draw_entities(this_room)
        self.draw_bullets(this_room)
        self.draw_belle(this_room)
        self.draw_weapon(this_room)
        return this_room

    def update_sprites(self):
        self.find_belle().weapons[0].bullets_group.update()
        self.find_belle().weapons[0].update()
        self.entities_group.update(self.obstacles_group, self.entities_group, self.image.get_rect()[-2:])
