import os
import shutil
import sqlite3
import time

import pygame

from executables.collectables.Battery import Battery
from executables.collectables.Coin import Coin
from executables.collectables.CyclotronDecoy import CyclotronDecoy
from executables.collectables.FanDecoy import FanDecoy
from executables.collectables.Powerup import Powerup
from executables.collectables.VacuumCleanerDecoy import VacuumCleanerDecoy
from executables.entities.Belle import Belle
from executables.entities.enemies.Catterfield import Catterfield
from executables.entities.enemies.Dispenser import Dispenser
from executables.entities.enemies.Dust import Dust
from executables.rooms.Hall import Hall
from executables.rooms.Room import Room
from executables.rooms.obstacles.Fridge import Fridge
from executables.rooms.obstacles.Sofa import Sofa
from executables.ui.widgets.tablets.EnergyTransaction import EnergyTransaction
from executables.ui.widgets.tablets.HealthIncrease import HealthIncrease
from executables.ui.widgets.tablets.MoneyRain import MoneyRain
from modules.collectiontools import uri_from_path


class R:
    def __init__(self, useful_size, real_size):
        if not os.path.exists(p := os.getenv("LOCALAPPDATA") + "/Fan/script.sqlite"):
            try:
                os.mkdir(os.getenv("LOCALAPPDATA") + "/Fan")
            except FileExistsError:
                pass
            shutil.copy(uri_from_path("../data/script.sqlite"), p)
        self.database = sqlite3.connect(p)
        self.query = self.database.cursor().execute
        self.useful_size = useful_size
        self.real_size = real_size
        self.coefficient = useful_size[0] / 3840
        self.mixer_playstart = time.time()
        self.mixer_playtime = lambda: (time.time() - self.mixer_playstart) % 121
        self.language = str()
        self.observe_language()
        self.drawable_dictionary = dict()
        self.reload_drawables()
        self.string_dictionary = dict()
        self.reload_strings()
        self.sound_dictionary = dict()
        self.reload_sounds()
        self.constant_dictionary = {
            "scrollbar_padding": 40 * self.coefficient,
            "store_offset_x": 712 * self.coefficient,
            "store_offset_y": 896 * self.coefficient,
            "store_padding": 784 * self.coefficient,
            "battery_equivalent": 10,
            "coefficient": self.coefficient,
            "useful_width": self.useful_size[0],
            "useful_height": self.useful_size[1],
            "real_offset_y": abs(self.useful_size[1] - self.real_size[1]) / 2,
            "real_offset_x": abs(self.useful_size[0] - self.real_size[0]) / 2,
            "health_bar_offset": 40 * self.coefficient,
            "health_bar_padding": 120 * self.coefficient,
            "scroll_bar_padding": 106 * self.coefficient,
            "room_object_to_id": {
                Room: 1,
                Hall: 2
            },
            "id_to_room_object": dict(),
            "obstacle_collectable_object_to_id": {
                Fridge: 1,
                Coin: 2,
                Powerup: 3,
                VacuumCleanerDecoy: 4,
                FanDecoy: 5,
                CyclotronDecoy: 6,
                Battery: 7,
                Sofa: 8
            },
            "id_to_obstacle_collectable_object": dict(),
            "entity_object_to_id": {
                Belle: 1,
                Catterfield: 2,
                Dispenser: 3,
                Dust: 4
            },
            "id_to_entity_object": dict(),
            "catalyst_object_to_id": {
                HealthIncrease: 1,
                MoneyRain: 2,
                EnergyTransaction: 3
            },
            "id_to_catalyst_object": dict()
        }
        for variable in ("room", "obstacle_collectable", "entity", "catalyst"):
            for key, value in self.constant_dictionary[f"{variable}_object_to_id"].items():
                self.constant_dictionary[f"id_to_{variable}_object"][value] = key
        self.color_dictionary = {
            "sad_gray": pygame.Color(10, 10, 10),
            "air_bullet_filling": pygame.Color(160, 144, 137)
        }

    def are_there_data(self):
        return bool(self.query("SELECT * FROM floor").fetchall())

    def observe_language(self):
        self.language = self.query("SELECT language FROM settings").fetchall()[0][0]

    def reload_strings(self):
        self.observe_language()
        for key, value in map(lambda elem: elem.strip().split(',', 1),
                              open(uri_from_path(f"../data/media/strings/{self.language}.csv"), 'r', encoding="utf-8")):
            self.string_dictionary[key] = value

    def reload_sounds(self):
        for elem in os.listdir(directory := uri_from_path("../data/media/sounds")):
            self.sound_dictionary[elem.split('.')[0]] = pygame.mixer.Sound(f"{directory}/{elem}")

    def sound(self, name):
        self.sound_dictionary[name].stop()
        self.sound_dictionary[name].play()

    def reload_drawables(self):
        self.observe_language()
        for elem in os.listdir(directory := uri_from_path("../data/media/images")):
            if self.language.upper() not in elem:
                continue
            self.drawable_dictionary['_'.join(elem.split('_')[:-1])] = pygame.transform.smoothscale(
                (im := pygame.image.load(f"{directory}/{elem}")),
                (im.get_width() * self.coefficient, im.get_height() * self.coefficient))

    def drawable(self, name):
        return self.drawable_dictionary[name]

    def constant(self, name):
        return self.constant_dictionary[name]

    def string(self, name):
        return self.string_dictionary[name]

    def color(self, name):
        return self.color_dictionary[name]

    def set_ventilation_state(self, is_opened, loudness_control_function, fade_time=int()):
        pygame.mixer.music.unload()
        pygame.mixer.music.load(uri_from_path(f"../data/media/sounds/{"OpenedVentilation" if is_opened else "ClosedVentilation"}.mp3"))
        loudness_control_function()
        pygame.mixer.music.play(-1, fade_ms=fade_time)
        pygame.mixer.music.set_pos(self.mixer_playtime())
