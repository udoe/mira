#
# MIRa - Minimalist Internet Radio
#
# Dependencies:
#   pip install guizero
#
#

"""
MIRa - Minimalist Internet Radio
"""

from typing import Any, AnyStr

import platform
import argparse
import guizero

from mira_config import MiraConfig
from mira_stations import MiraStations
from constants import Key



def get_stations_list(stations: MiraStations) -> list:
    """ Validate specified stations and return a stations list. """
    st_list = []
    for st in stations.stations:
        if Key.URL in st and st[Key.URL]:
            st_list.append(st)

    return st_list




class Preset:
    """ A predefined internet radio station """

    def __init__(self, station: dict) -> None:
        self.name = station[Key.NAME]
        self.url = station[Key.URL]




class MiraAppplication:
    """ Top level application """

    def __init__(self, config: MiraConfig, stations: MiraStations) -> None:
        # build list of presets from predefined stations list
        st_list = get_stations_list(stations)
        self.presets = []
        for st in st_list:
            self.presets.append(Preset(st))

        # top level window
        app_width = config.Display.WIDTH
        app_height = config.Display.HEIGHT
        self.app = guizero.App(
                            title="MIRa",
                            width=app_width,
                            height=app_height
                            )

        # status pane
        self.status_box = guizero.Box(
                                self.app,
                                align="top",
                                width="fill"
                                )
        self.status_box.bg = config.Status.BACKGROUND_COLOR
        self.status_text1 = guizero.Text(
                                self.status_box,
                                font=config.Status.FONT[0],
                                size=config.Status.FONT[1],
                                color=config.Status.TEXT_COLOR,
                                text="line 1"
                                )
        self.status_text2 = guizero.Text(
                                self.status_box,
                                font=config.Status.FONT[0],
                                size=config.Status.FONT[1],
                                color=config.Status.TEXT_COLOR,
                                text="line 2"
                                )

        # spacing area (optional)
        spacing_height = int(config.Spacing.HEIGHT)
        if spacing_height > 0:
            self.spacing_box = guizero.Box(
                                    self.app,
                                    align="top",
                                    width="fill",
                                    height=spacing_height
                                    )
            self.spacing_box.bg = config.Spacing.BACKGROUND_COLOR

        # box that contains the buttons
        self.buttons_box = guizero.Box(
                                self.app,
                                align="top",
                                width=app_width,
                                height="fill",
                                layout="grid"
                                )

        # create a button for each preset
        buttons_per_row = int(config.Buttons.NUM_BUTTONS_PER_ROW)
        bt_width = int(app_width / buttons_per_row)
        bt_height = int(config.Buttons.BUTTON_HEIGHT)
        bt_x = 0
        bt_y = 0
        self.preset_buttons = []
        for ps in self.presets:
           # To be able to size a button in terms of pixels (instead characters),
           # we put every button in a surrounding box.
           box_width = bt_width
           bx = guizero.Box(
                        self.buttons_box,
                        grid=[bt_x, bt_y],
                        width=box_width,
                        height=bt_height
                        )
           bt = guizero.PushButton(
                        bx,
                        width="fill",
                        height="fill",
                        text=ps.name,
                        command=lambda:self._button_pressed(),
                        )
           bt.font = config.Buttons.FONT[0]
           bt.text_size = config.Buttons.FONT[1]
           bt.bg = config.Buttons.BACKGROUND_COLOR
           bt.text_color = config.Buttons.TEXT_COLOR

           self.preset_buttons.append(bt)

           bt_x += 1
           if bt_x >= buttons_per_row:
               bt_x = 0
               bt_y += 1

        # remove title bar (works on Linux only)
        if platform.system() is 'Linux':
            root = self.app.tk
            root.wm_attributes('-type', 'splash')



    def _button_pressed(self, preset: Preset) -> None:
        print("button {} was pressed".format(preset.name))


    def run(self) -> None:
        self.app.display()




def main():
    app = MiraAppplication(MiraConfig, MiraStations)
    app.run()


if __name__ == "__main__":
    main()
