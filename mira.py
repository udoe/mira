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
import pathlib
import math

from mira_config import MiraConfig
from mira_stations import MiraStations
from constants import Key

from helpers import Preset, PresetButton, PageButton, ensure_dir_exists, get_stations_list



class MiraAppplication:
    """ Top level application """


    def __init__(self, config: MiraConfig, stations: MiraStations, fullscreen: bool) -> None:

        self.config = config
        self.timer_running = False

        self.preset_buttons = []
        self.page_buttons = []

        # build list of presets from predefined stations list
        st_list = get_stations_list(stations)
        self.presets = []
        n = 0
        for st in st_list:
            self.presets.append(Preset(n, config, st))
            n += 1
        
        # if no stations are defined, add a default station
        if len(self.presets) == 0:
            dummy_st = dict(
                name = "Radio 1",
                url = "https://radio1.de"
                )
            dummy_preset = Preset(0, config, dummy_st)
            self.presets.append(dummy_preset)

        # restore last station or None
        self.current_preset = self._load_last_played()

        # top level window
        self.app = guizero.App(
                            title="MIRa",
                            width=config.Display.WIDTH,
                            height=config.Display.HEIGHT
                            )
        
        if fullscreen:
            self.app.set_full_screen()

        logging.info(f"App window: width={self.app.width}, height={self.app.height}")

        # title bar
        self._create_title_bar()

        # status pane
        self._create_status_box()

        # spacing area (optional)
        self._create_spacing_area(self.config.Spacing.HEIGHT)

        # create box for preset buttons
        self.buttons_box = guizero.Box(
                                self.app,
                                align="top",
                                width="fill",
                                height=(self.config.Buttons.BUTTON_HEIGHT * self.config.Buttons.NUM_BUTTON_ROWS),
                                layout="grid"
                                )
        
        logging.info(f"Preset buttons box: width={self.buttons_box.width}, height={self.buttons_box.height}")

        # create buttons within the preset buttons box
        self._create_buttons_page(self._get_current_page_index())

        # box that contains the page selector buttons
        self._create_page_selector()



    # Functions:
    def _create_title_bar(self) -> None:
        self.title_bar = guizero.Box(
                                self.app,
                                align="top",
                                width="fill",
                                height=self.config.Title.HEIGHT
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
                                align="right"
                                )


    def _create_status_box(self) -> None:
        status_box_height = self.config.Status.HEIGHT
        status_line_height = int(status_box_height / 2)
        self.status_box = guizero.Box(
                                self.app,
                                align="top",
                                width="fill",
                                height=status_box_height
                                )
        self.status_box.bg = self.config.Status.BACKGROUND_COLOR
        self.status_box1 = guizero.Box(
                                self.status_box,
                                align="top",
                                width="fill",
                                height=(status_line_height + 4)
                                )
        self.status_box2 = guizero.Box(
                                self.status_box,
                                align="top",
                                width="fill",
                                height=(status_line_height - 4)
                                )
        self.status_text1 = guizero.Text(
                                self.status_box1,
                                height="fill",
                                align="bottom",
                                font=self.config.Status.FONT_LINE1[0],
                                size=self.config.Status.FONT_LINE1[1],
                                color=self.config.Status.TEXT_COLOR
                                )
        self.status_text2 = guizero.Text(
                                self.status_box2,
                                height="fill",
                                align="bottom",
                                font=self.config.Status.FONT_LINE2[0],
                                size=self.config.Status.FONT_LINE2[1],
                                color=self.config.Status.TEXT_COLOR
                                )


    def _create_spacing_area(self, height: int) -> None:
        if height > 0:
            spacing_box = guizero.Box(
                                    self.app,
                                    align="top",
                                    width="fill",
                                    height=height
                                    )
            spacing_box.bg = self.config.Spacing.BACKGROUND_COLOR


    def _create_buttons_page(self, page_idx: int) -> None:

        # reset
        self.preset_buttons = []
        logging.info(f"--- preset buttons box cleanup ---")
        logging.info(f"All button box children before destroy: {self.buttons_box.children}")
        while len(self.buttons_box.children) > 0:
            self.buttons_box.children[0].destroy()
        logging.info(f"All button box children after destroy: {self.buttons_box.children}")

        # create a button for each preset of the given page
        bt_x = 0
        bt_y = 0
        for idx in range(0, self._get_num_presets_of_page(page_idx)):

            ps = self.presets[self._get_first_preset_idx_of_page(page_idx) + idx]
            bt = PresetButton(
                    containing_box=self.buttons_box, 
                    position=(bt_x, bt_y),
                    preset=ps,
                    callback=self._on_button_pressed,
                    config=self.config
                    )

            self.preset_buttons.append(bt)
            logging.info(f"Placed preset button on grid at: x={bt_x}, y={bt_y}")

            bt_x += 1
            if bt_x >= self.config.Buttons.NUM_BUTTON_COLUMNS:
                bt_x = 0
                bt_y += 1



    def _create_page_selector(self):
        # init
        self.selector_box = guizero.Box(
                                self.app,
                                align="bottom",
                                width="fill",
                                height=self.config.PageSelector.BUTTON_HEIGHT,
                                layout="grid"
                                )
        self.page_buttons = []

        # add buttons to box
        bt_y = 0
        bt_x = 0
        for page_idx in range(0, self._get_num_pages()):
  
            bt = PageButton(
                    containing_box=self.selector_box,
                    position=(bt_x, bt_y),
                    page_idx=page_idx,
                    callback=self._on_page_selected,
                    config=self.config
                    )

            self.page_buttons.append(bt)

            bt_x += 1


    def _get_current_page_index(self) -> int:
        if self.current_preset is not None:
            return math.floor(self.current_preset.number / self.config.Buttons.NUM_BUTTONS_PER_PAGE)
        return 0
    
    def _get_first_preset_idx_of_page(self, page_idx: int) -> int:
        return page_idx * self.config.Buttons.NUM_BUTTONS_PER_PAGE

    def _get_num_presets_of_page(self, page_idx: int) -> int:
        cnt = len(self.presets) - self._get_first_preset_idx_of_page(page_idx)
        if cnt > self.config.Buttons.NUM_BUTTONS_PER_PAGE:
            cnt = self.config.Buttons.NUM_BUTTONS_PER_PAGE
        return cnt
    
    def _get_num_pages(self) -> int:
        return math.ceil(len(self.presets) / self.config.Buttons.NUM_BUTTONS_PER_PAGE)



    def _on_page_selected(self, page_idx: int) -> None:
        logging.info(f"Page '{page_idx}' was selected.")

        self._create_buttons_page(page_idx)
        self._update_page_btn_color(page_idx)
        self._update_btn_color(self.current_preset)


    def _on_button_pressed(self, preset: Preset) -> None:
        logging.info(f"Button '{preset.name}' was pressed. URL: '{preset.url}'")
        self.current_preset = preset

        self._play(preset)

        # change color of pressed button
        self._update_btn_color(preset)

        # save state
        self._save_last_played(preset)


    def _update_btn_color(self, preset: Preset) -> None:
        for btn in self.preset_buttons:
            if btn.preset.number == preset.number:
                btn.button.bg = self.config.Buttons.PRESSED_BUTTON_COLOR
            else:
                btn.button.bg = self.config.Buttons.BACKGROUND_COLOR


    def _update_page_btn_color(self, page_idx: int) -> None:
        for btn in self.page_buttons:
            if btn.idx == page_idx:
                btn.button.bg = self.config.PageSelector.PRESSED_BUTTON_COLOR
            else:
                btn.button.bg = self.config.PageSelector.BACKGROUND_COLOR


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

        self.title_bar_date.value = " " + date
        self.title_bar_time.value = time

        quality = self._get_wifi_quality()
        if quality >= 0:
            self.title_bar_signal.value = f"WiFi: {quality}%" + " "
        else:
            self.title_bar_signal.value = ""


    def _get_wifi_quality(self) -> int:
        try:
            cmd = ["iwconfig", "wlan0"]
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout
        except Exception as e:
            logging.error(f"Failed to execute {cmd} : {e}")
            return -1

        # Link Quality=50/70  Signal level=-60 dBm
        search_string = "Link Quality="
        for line in output.splitlines():
            pos = line.find(search_string)
            if pos >= 0:
                start = pos + len(search_string)
                end = line.find(" ", start)
                if end >= 0:
                    value = line[start:end]
                    value_list = value.split('/')
                    if len(value_list) >= 2:
                        sig_qual = int(value_list[0])
                        max_qual = int(value_list[1])
                        quality = int(round((sig_qual * 100) / max_qual, 0))
                        return quality

        return -1


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
            logging.info(f"mpc returned: '{output}'")
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


    def _get_saved_state_file(self) -> pathlib.Path:
        filepath = pathlib.Path(self.config.General.SAVED_STATE_FILE)
        filepath = filepath.expanduser()
        return filepath


    def _load_last_played(self) -> Preset|None:
        filepath = self._get_saved_state_file()
        try:
            with open(filepath, "r") as infile:
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
        filepath = self._get_saved_state_file()
        ensure_dir_exists(filepath)
        try:
            with open(filepath, "w") as outfile:
                json.dump(data, outfile)
        except Exception as e:
            logging.error(f"Couldn't save state. {e}")


    def _restore_last_played(self) -> None:
        if self.current_preset is not None:
            self._play(self.current_preset)
            self._update_btn_color(self.current_preset)
            self._update_page_btn_color(self._get_current_page_index())
        else:
            self.status_text1.value = "No preset active."


    def run(self) -> None:
        logging.info(f"--- restoring last played station ---")
        self._restore_last_played()

        self._update_title_bar()
        self.app.repeat(self.config.Title.UPDATE_INTERVAL, self._on_title_timer)

        logging.info(f"App window before display(): width={self.app.width}, height={self.app.height}")

        self.app.display()






def main(fullscreen: bool):
    logfile = pathlib.Path(MiraConfig.General.LOGFILE)
    logfile = logfile.expanduser()
    ensure_dir_exists(logfile)

    logging.basicConfig(
        filename=str(logfile),
        encoding='utf-8',
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
        )
    if MiraConfig.General.LOGLEVEL_DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info(f"--- initializing ---")
    logging.info(f"--- guizero version {guizero.__version__} ---")
    app = MiraAppplication(MiraConfig, MiraStations, fullscreen)
    logging.info(f"--- app startup ---")
    app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='show the app in fullscreen mode'
        )
    args = parser.parse_args()

    main(args.fullscreen)
