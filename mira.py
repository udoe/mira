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
import subprocess
import logging
import json

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


def running_on_linux() -> bool:
    return platform.system() == 'Linux'


def running_on_windows() -> bool:
    return platform.system() == 'Windows'



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




class MiraAppplication:
    """ Top level application """

    def __init__(self, config: MiraConfig, stations: MiraStations) -> None:
        
        self.mpc_path = config.General.MPC_PATH
        self.saved_state_filename = config.General.SAVED_STATE_FILENAME
        self.initial_update_interval = config.Status.INITAL_UPDATE_INTERVAL
        self.update_interval = config.Status.UPDATE_INTERVAL

        # build list of presets from predefined stations list
        st_list = get_stations_list(stations)
        self.presets = []
        n = 0
        for st in st_list:
            self.presets.append(Preset(n, config, st))
            n += 1

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
                                color=config.Status.TEXT_COLOR
                                )
        self.status_text2 = guizero.Text(
                                self.status_box,
                                font=config.Status.FONT[0],
                                size=config.Status.FONT[1],
                                color=config.Status.TEXT_COLOR
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
                        command=self._button_pressed,
                        args=[ps],
                        )
            bt.font = config.Buttons.FONT[0]
            bt.text_size = config.Buttons.FONT[1]
            bt.bg = ps.background_color    
            bt.text_color = ps.text_color
            
            self.preset_buttons.append(bt)

            bt_x += 1
            if bt_x >= buttons_per_row:
                bt_x = 0
                bt_y += 1


    def _button_pressed(self, preset: Preset) -> None:
        logging.info(f"Button '{preset.name}' was pressed. URL: '{preset.url}'")
        
        self._play(preset)

        # save state
        self._save_last_played(preset)        


    def _play(self, preset: Preset) -> None:    
        # stop refresh timer
        self.app.cancel(self._timer_event)
        
        # clear playlist
        self._execute_mpc(["clear"])
        # add url
        self._execute_mpc(["add", preset.url])
        # play playlist
        self._execute_mpc(["play"])
        
        # update status line
        self.status_text1.value = preset.name
        self.status_text2.value = ""

        # start refresh timer
        self.app.after(self.initial_update_interval, self._timer_event)


    def _timer_event(self) -> None:
        text = self._get_song_info()
        parts = text.split(':')
        if len(parts) > 1:
            line2 = parts[1]
        else:
            line2 = text
        self.status_text2.value = line2.strip()
        self.app.after(self.update_interval, self._timer_event)


    def _get_song_info(self) -> str:       
            output = self._execute_mpc(["current"])
            logging.info(f"stdout: '{output}'")
            return output


    def _execute_mpc(self, args: list[str]) -> str:
        try:    
            mpc = self.mpc_path
            cmd = [mpc] + args
            logging.info(f"executing: {cmd}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            return process.stdout
        except Exception as e:
            logging.error(f"Failed to execute {cmd} : {e}")
            return str()


    def _load_last_played(self) -> Preset|None:
        try:
            with open(self.saved_state_filename, "r") as infile:
                data = json.load(infile)
        except Exception as e:
            logging.info(f"State file doesn't exist yet. {e}")
            return None

        if Key.PRESET_NUMBER in data:
            number = data[Key.PRESET_NUMBER]
            if number < len(self.presets):
                preset = self.presets[number]
                return preset
        
        return None


    def _save_last_played(self, preset: Preset) -> None:
        data = {
            Key.PRESET_NUMBER : preset.number,
            "station_name" : preset.name
        }
        try:
            with open(self.saved_state_filename, "w") as outfile:
                json.dump(data, outfile)
        except Exception as e:
            logging.info(f"Couldn't save state. {e}")
            

    def _restore_last_played(self) -> None:
        preset = self._load_last_played()
        if preset is not None:
            self._play(preset)
        else:
            self.status_text1.value = "No preset active."



    def run(self, fullscreen: bool) -> None:
        self._restore_last_played()

        if fullscreen:
            self.app.set_full_screen()
        
        self.app.display()




def main(fullscreen: bool):
    logging.basicConfig(
        filename='mira.log', 
        encoding='utf-8', 
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    app = MiraAppplication(MiraConfig, MiraStations)
    app.run(fullscreen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fullscreen', 
        action='store_true',
        help='show the app in fullscreen mode'
        )
    args = parser.parse_args()

    main(args.fullscreen)
