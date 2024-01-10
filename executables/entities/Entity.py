import pygame
import time


from modules.animation import Animated


class Entity(pygame.sprite.Sprite, Animated):
    def __init__(self, r, animation_name, animation_period, *sprite_groups):
        super().__init__(*sprite_groups)
        pygame.sprite.Sprite.__init__(self, *sprite_groups)
        Animated.__init__(self, r, animation_name, animation_period)
        self.r = r
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = (self.r.constant("useful_width") / 2 - self.rect.width / 2,
                                    self.r.constant("useful_height") / 2 - self.rect.height / 2)
        self.energy = 100
        self.speed = 1 * self.r.constant("coefficient")
        self.damaging_bullets = dict()
        self.last_delta_x = float()
        self.last_delta_y = float()
        self.x, self.y = self.rect[:2]

    def add_damaging_bullet(self, bullet):
        if bullet not in self.damaging_bullets:
            self.damaging_bullets[bullet] = pygame.time.Clock()

    def remove_damaging_bullet(self, bullet=None):
        if bullet:
            del self.damaging_bullets[bullet]
        else:
            for key in list(self.damaging_bullets.keys()):
                if not key.alive():
                    del self.damaging_bullets[key]

    def undo_move_x(self):
        self.rect.x -= int(self.last_delta_x)
        self.x -= self.last_delta_x

    def undo_move_y(self):
        self.rect.y -= int(self.last_delta_y)
        self.y -= self.last_delta_y

    def redo_move_x(self):
        self.rect.x += int(self.last_delta_x)
        self.x += self.last_delta_x

    def redo_move_y(self):
        self.rect.y += int(self.last_delta_y)
        self.y += self.last_delta_y

    def update(self, *args):
        self.play_animation()

