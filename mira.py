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
import datetime

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

        self.config = config
        self.timer_running = False

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
        

        # title bar
        self._create_title_bar()


        # status pane
        self._create_status_box()


        # spacing area (optional)
        self._create_spacing_area()


        # box that contains the buttons
        self._create_buttons()
    
    
    # Functions:
    def _create_title_bar(self) -> None:
        self.title_bar = guizero.Box(
                                self.app,
                                align="top",
                                width="fill",
                                height=40
                                )
        self.title_bar.bg = self.config.Title.BACKGROUND_COLOR
        self.title_bar_left = guizero.Box(
                                self.title_bar,
                                align="left",
                                width=int(self.config.Display.WIDTH/3),
                                height=20
                                )
        self.title_bar_center = guizero.Box(
                                self.title_bar,
                                align="left",
                                width=int(self.config.Display.WIDTH/3),
                                height=20
                                )
        self.title_bar_right = guizero.Box(
                                self.title_bar,
                                align="left",
                                width=int(self.config.Display.WIDTH/3),
                                height=20
                                )
        self.title_bar_date = guizero.Text(
                                self.title_bar_left,
                                align="left"
                                )
        self.title_bar_time = guizero.Text(
                                self.title_bar_center,
                                text="Time"
                                )
        self.title_bar_signal = guizero.Text(
                                self.title_bar_right,
                                align="right",
                                )

    
    def _create_status_box(self) -> None:
        self.status_box = guizero.Box(
                                self.app,
                                align="top",
                                width="fill"
                                )
        self.status_box.bg = self.config.Status.BACKGROUND_COLOR
        self.status_text1 = guizero.Text(
                                self.status_box,
                                font=self.config.Status.FONT[0],
                                size=self.config.Status.FONT[1],
                                color=self.config.Status.TEXT_COLOR
                                )
        self.status_text2 = guizero.Text(
                                self.status_box,
                                font=self.config.Status.FONT[0],
                                size=self.config.Status.FONT[1],
                                color=self.config.Status.TEXT_COLOR
                                )


    def _create_spacing_area(self) -> None:
        spacing_height = int(self.config.Spacing.HEIGHT)
        if spacing_height > 0:
            self.spacing_box = guizero.Box(
                                    self.app,
                                    align="top",
                                    width="fill",
                                    height=spacing_height
                                    )
            self.spacing_box.bg = self.config.Spacing.BACKGROUND_COLOR


    def _create_buttons(self) -> None:
        self.buttons_box = guizero.Box(
                                self.app,
                                align="top",
                                width=self.config.Display.WIDTH,
                                height="fill",
                                layout="grid"
                                )

        # create a button for each preset
        buttons_per_row = int(self.config.Buttons.NUM_BUTTONS_PER_ROW)
        bt_width = int(self.config.Display.WIDTH / buttons_per_row)
        bt_height = int(self.config.Buttons.BUTTON_HEIGHT)
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
            bt.font = self.config.Buttons.FONT[0]
            bt.text_size = self.config.Buttons.FONT[1]
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
        if self.timer_running:
            self.app.cancel(self._on_status_timer)
            self.timer_running = False
        
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
        self.app.after(self.config.Status.INITAL_UPDATE_INTERVAL, self._on_status_timer)
        self.timer_running = True


    def _on_status_timer(self) -> None:
        self._update_status()
        self.app.after(self.config.Status.UPDATE_INTERVAL, self._on_status_timer)

    
    def _on_title_timer(self) -> None:
        self._update_title_bar()


    def _update_title_bar(self) -> None:
        dt = datetime.datetime.now()
        date = dt.strftime('%a %d %b %Y')
        if self.config.Title.USE_24h_TIME_FORMAT:
            time = dt.strftime('%H:%M')
        else:
            time = dt.strftime('%I:%M %p')

        self.title_bar_date.value = date
        self.title_bar_time.value = time


    def _get_wifi_quality(self) -> None:
        cmd = ["iwconfig", "wlan0"]
        process = subprocess.run(cmd, capture_output=True, text=True)
        output = process.stdout
        

    def _update_status(self) -> None:
        text = self._get_song_info()
        parts = text.split(':')
        if len(parts) > 1:
            line2 = parts[1]
        else:
            line2 = text
        self.status_text2.value = line2.strip()


    def _get_song_info(self) -> str:       
            output = self._execute_mpc(["current"])
            logging.info(f"stdout: '{output}'")
            return output


    def _execute_mpc(self, args: list[str]) -> str:
        try:    
            mpc = self.config.General.MPC_PATH
            cmd = [mpc] + args
            logging.info(f"executing: {cmd}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            return process.stdout
        except Exception as e:
            logging.error(f"Failed to execute {cmd} : {e}")
            return str()


    def _load_last_played(self) -> Preset|None:
        try:
            with open(self.config.General.SAVED_STATE_FILENAME, "r") as infile:
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
            with open(self.config.General.SAVED_STATE_FILENAME, "w") as outfile:
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

        self._update_title_bar()
        self.app.repeat(self.config.Title.UPDATE_INTERVAL, self._on_title_timer)
        
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
