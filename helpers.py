from typing import Any, AnyStr


import guizero
import logging
import math
import pathlib
from mira_stations import MiraStations


from mira_config import MiraConfig
from constants import Key


def ensure_dir_exists(filepath: pathlib.Path) -> None:
    p = filepath.parent
    p.mkdir(parents=True, exist_ok=True)


def get_stations_list(stations: MiraStations) -> list:
    """ Validate specified stations and return a stations list. """
    st_list = []
    for st in stations.stations:
        if Key.URL in st and st[Key.URL]:
            st_list.append(st)

    return st_list





class Preset:
    """ A predefined internet radio station """

    def __init__(self, number: int, config: MiraConfig, station: dict) -> None:
        self.number = number
        self.name = station[Key.NAME]
        self.url = station[Key.URL]

        if Key.BACKGROUND_COLOR in station:
            self.background_color = station[Key.BACKGROUND_COLOR]
        else:
            self.background_color = config.Buttons.BACKGROUND_COLOR

        if Key.TEXT_COLOR in station:
            self.text_color = station[Key.TEXT_COLOR]
        else:
            self.text_color = config.Buttons.TEXT_COLOR


class PresetButton:

    def __init__(self, containing_box: guizero.Box, position: tuple, preset: Preset, callback: Any, config: MiraConfig) -> None:

        self.preset = preset

        bt_width = math.floor(config.Display.WIDTH / config.Buttons.NUM_BUTTON_COLUMNS)
        # - 4: workaround for last button row spilling its clickable area below and onto the page selectors containg box
        bt_height = config.Buttons.BUTTON_HEIGHT - 4

        # To be able to size a button in terms of pixels (instead characters),
        # we put every button in a surrounding box.
        box = guizero.Box(
                        master=containing_box,
                        grid=[position[0], position[1]],
                        width=bt_width,
                        height=bt_height,
                        )
        self.button = guizero.PushButton(
                        master=box,
                        width="fill",
                        height="fill",
                        text=preset.name,
                        command=callback,
                        args=[preset]
                        )
        self.button.font = config.Buttons.FONT[0]
        self.button.text_size = config.Buttons.FONT[1]
        self.button.bg = preset.background_color
        self.button.text_color = preset.text_color

        logging.info(f"PresetButton: '{self.button.text}', width={self.button.width}, height={self.button.height}")



class PageButton:

    def __init__(self, containing_box: guizero.Box, position: tuple, page_idx: int, callback: Any, config: MiraConfig) -> None:

        self.idx = page_idx

        bt_width = config.PageSelector.BUTTON_WIDTH
        bt_height = config.PageSelector.BUTTON_HEIGHT

        # To be able to size a button in terms of pixels (instead characters),
        # we put every button in a surrounding box.
        box = guizero.Box(
                        master=containing_box,
                        grid=[position[0], position[1]],
                        width=bt_width,
                        height=bt_height
                        )
        self.button = guizero.PushButton(
                        master=box,
                        width="fill",
                        height="fill",
                        text=f"{self.idx+1}",
                        command=callback,
                        args=[self.idx]
                        )
        self.button.font = config.PageSelector.FONT[0]
        self.button.text_size = config.PageSelector.FONT[1]
        self.button.bg = config.PageSelector.BACKGROUND_COLOR
        self.button.text_color = config.PageSelector.TEXT_COLOR
