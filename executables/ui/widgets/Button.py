import pygame

from executables.ui.widgets.InteractiveWidget import InteractiveWidget
from modules.collectiontools import uri_from_path


class Button(InteractiveWidget):
    def __init__(self, r, label, pos, action, is_icon=False, is_enabled=True):
        super().__init__(r, pos, action, is_enabled)
        self.is_icon = is_icon
        self.is_enabled = is_enabled
        self.label = None
        self.rebuild_label(label)
        self.chuncks = int()
        self.calculate_size()
        self.image = pygame.Surface((0, 0))

    def rebuild_label(self, label):
        self.label = pygame.font.Font(uri_from_path("../data/media/fonts/AmaticSC-Regular.ttf"),
                                      int(125 * self.r.constant("coefficient"))) \
            .render(label, 1, pygame.Color("black"))

    def calculate_size(self):
        if self.focus and self.is_enabled:
            string_start = "button_focused"
        else:
            string_start = "button_unfocused"
        addition = sum(self.r.drawable(elem).get_width() for elem in
                       (f"{string_start}_left_cap", f"{string_start}_right_cap"))
        self.chuncks = max(self.label.get_width() // self.r.drawable(string_start).get_width(),
                           0 if self.is_icon else 1)
        self.xx = self.x + addition + self.chuncks * self.r.drawable(string_start).get_width()
        self.yy = self.y + self.r.drawable(string_start).get_height()

    def build_surface(self):
        surface = pygame.Surface((self.xx - self.x, self.yy - self.y), pygame.SRCALPHA, 32)
        if self.focus and self.is_enabled:
            string_start = "button_focused"
        else:
            string_start = "button_unfocused"
        left_cap = self.r.drawable(f"{string_start}_left_cap")
        surface.blit(left_cap, (0, 0))
        for i in range(self.chuncks):
            surface.blit(self.r.drawable(string_start), (left_cap.get_width() +
                                                         self.r.drawable(string_start).get_width() * i, 0))
        surface.blit(self.r.drawable(f"{string_start}_right_cap"),
                     (left_cap.get_width() + self.r.drawable(string_start).get_width() * self.chuncks, 0))
        surface.blit(self.label, (surface.get_width() * 0.5 - self.label.get_width() * 0.5,
                                  surface.get_height() * 0.5 - self.label.get_height() * 0.5))
        if not self.is_enabled:
            surface.fill(pygame.Color(100, 100, 100), special_flags=pygame.BLEND_MULT)
        self.image = surface
        
    def draw(self, surface):
        self.build_surface()
        super().draw(surface)
        
