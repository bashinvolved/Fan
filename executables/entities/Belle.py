import math
import time
import pygame

from executables.entities.Entity import Entity
from executables.ui.widgets.Scrollbar import Scrollbar
from executables.ui.widgets.tablets.HealthIncrease import HealthIncrease
from executables.ui.widgets.tablets.MoneyRain import MoneyRain
from executables.ui.widgets.tablets.EnergyTransaction import EnergyTransaction


class Belle(Entity):
    def __init__(self, r, animation_name, animation_period, *sprite_groups):
        super().__init__(r, animation_name, animation_period, *sprite_groups)
        self.weapons = list()
        self.mouse_position_compensation_x = int()
        self.mouse_position_compensation_y = int()
        self.mouse_position_x, self.mouse_position_y = pygame.mouse.get_pos()
        self.x_move_time = UselessClock()
        self.y_move_time = UselessClock()
        self.x_movement = int()
        self.y_movement = int()
        self.ghost_time = 2000000000
        self.mouse_updated = True
        self.became_ghost_at = None
        self.money = int()
        self.catalysts = Scrollbar(self.r, (1322, 1038), lambda: None, 1200, 890)
        self.money_multiplier = 1
        self.apply_catalysts()

    def add_money(self, value):
        self.money += value * self.money_multiplier

    def apply_catalysts(self):
        if HealthIncrease in self.catalysts.enumerate_classes() and \
                not next(self.r.query("SELECT applied FROM catalyst WHERE id = 1"))[0]:
            self.energy_threshold += 2 * self.r.constant("battery_equivalent")
            self.r.query("UPDATE catalyst SET applied = 1 WHERE id = 1")
            self.r.database.commit()
        if MoneyRain in self.catalysts.enumerate_classes() and \
                not next(self.r.query("SELECT applied FROM catalyst WHERE id = 2"))[0]:
            self.money_multiplier += 1
            self.r.query("UPDATE catalyst SET applied = 1 WHERE id = 2")
            self.r.database.commit()
        if EnergyTransaction in self.catalysts.enumerate_classes() and \
                not next(self.r.query("SELECT applied FROM catalyst WHERE id = 3"))[0]:
            self.energy_threshold //= 2
            self.r.query("UPDATE catalyst SET applied = 1 WHERE id = 3")
            self.r.database.commit()

    def sort_weapon_by(self, criteria_class):
        if self.mouse_updated:
            self.mouse_updated = False
            self.weapons.sort(key=lambda elem: elem.__class__ == criteria_class, reverse=True)

    def aim_cursor(self):
        self.set_mouse_position()
        if self.rect.x + self.rect.width / 2 <= self.mouse_position_x and not self.animation_is_flipped:
            self.animation_is_flipped = True
            if self.weapons:
                self.weapons[0].animation_is_flipped = True
                self.weapons[0].play_animation(True)
            self.play_animation(True)
        elif self.rect.x + self.rect.width / 2 > self.mouse_position_x and self.animation_is_flipped:
            self.animation_is_flipped = False
            if self.weapons:
                self.weapons[0].animation_is_flipped = False
                self.weapons[0].play_animation(True)
            self.play_animation(True)

    def set_mouse_position(self):
        self.mouse_position_x, self.mouse_position_y = pygame.mouse.get_pos()
        self.mouse_position_x += self.mouse_position_compensation_x
        self.mouse_position_y += self.mouse_position_compensation_y

    def set_mouse_position_compensation(self, x, y):
        self.mouse_position_compensation_x, self.mouse_position_compensation_y = (x - self.r.constant("real_offset_x"),
                                                                                  y - self.r.constant("real_offset_y"))

    def use_weapon(self):
        if not self.weapons:
            return
        self.weapons[0].release_bullet((self.mouse_position_compensation_x,
                                        self.mouse_position_compensation_y),
                                       EnergyTransaction in self.catalysts.enumerate_classes())
        self.weapons[0].set_animation(f"{self.weapons[0].__class__.__name__.lower()}_attack", 100)

    def move(self):
        self.last_delta_x = self.x_move_time.tick() * self.x_movement * self.speed
        self.last_delta_y = self.y_move_time.tick() * self.y_movement * self.speed
        self.x += self.last_delta_x
        self.y += self.last_delta_y
        self.rect.x = self.x
        self.rect.y = self.y
        if self.weapons:
            self.weapons[0].rect.x = self.x
            self.weapons[0].rect.y = self.y
            self.weapons[0].apply_offset()
            self.weapons[0].play_animation()

    def start_moving(self, direction):
        if direction == "up":
            self.y_movement = -1
            self.y_move_time = pygame.time.Clock()
        elif direction == "down":
            self.y_movement = 1
            self.y_move_time = pygame.time.Clock()
        elif direction == "left":
            self.x_movement = -1
            self.x_move_time = pygame.time.Clock()
        elif direction == "right":
            self.x_movement = 1
            self.x_move_time = pygame.time.Clock()
        if "movement" not in self.animation_name:
            self.set_animation(f"{self.__class__.__name__.lower()}_movement")

    def stop_moving(self, direction):
        if direction == "up":
            if self.y_movement == -1:
                self.y_move_time = UselessClock()
        elif direction == "down":
            if self.y_movement == 1:
                self.y_move_time = UselessClock()
        elif direction == "left":
            if self.x_movement == -1:
                self.x_move_time = UselessClock()
        elif direction == "right":
            if self.x_movement == 1:
                self.x_move_time = UselessClock()
        if not (self.y_move_time.tick() + self.x_move_time.tick()) and "idle" not in self.animation_name:
            self.set_animation(f"{self.__class__.__name__.lower()}_idle")

    def damage(self):
        # return
        if self.damaging_bullets and not self.became_ghost_at:
            self.make_ghost()
        super().damage()
        
    def add_damaging_bullet(self, bullet):
        if not self.became_ghost_at:
            super().add_damaging_bullet(bullet)

    def damage_collision(self, entity):
        # return
        self.energy -= entity.collision_damage_rate
        self.make_ghost()

    def make_ghost(self):
        self.became_ghost_at = time.time_ns()

    def update_ghost_state(self):
        if self.became_ghost_at:
            if self.ghost_time < time.time_ns() - self.became_ghost_at:
                self.became_ghost_at = None
                return
            self.image = self.image.copy()
            self.image.set_alpha(arg := int(math.sin(time.time_ns() / 10 ** 7.8) * 255))
            if self.weapons:
                self.weapons[0].image = self.weapons[0].image.copy()
                self.weapons[0].image.set_alpha(arg)

    def update(self, *args):
        super().update()
        self.update_ghost_state()
        self.aim_cursor()
        self.move()


class UselessClock:
    def tick(self):
        return int()
