"""
Minimalist Internet Radio - config settings
"""

class MiraConfig:
    """ config settings """

    class General:
        MPC_PATH = "/usr/bin/mpc"
        SAVED_STATE_FILE = "~/.mira/mira_state.json"
        LOGFILE = "~/.mira/mira.log"
        LOGLEVEL_DEBUG = False

    class Display:
        """ display properties """
        WIDTH = 800
        HEIGHT = 480

    class Title:
        HEIGHT = 40
        USE_24h_TIME_FORMAT = True
        BACKGROUND_COLOR = "lightblue"
        UPDATE_INTERVAL = 5000

    class Status:
        """ status pane """
        FONT_LINE1 = ("Helvetica", 26)
        FONT_LINE2 = ("Helvetica", 24)

        # Specify a color name, for a complete list, check out https://wiki.tcl.tk/37701
        BACKGROUND_COLOR = "yellow"
        # Alternatively, specify (R, G, B) values, 0..255.
        #BACKGROUND_COLOR = (255, 0, 0)

        # Specify text color in a similar way.
        TEXT_COLOR = "black"

        # Status update in milliseconds
        INITAL_UPDATE_INTERVAL = 4000
        UPDATE_INTERVAL = 2000


    class Spacing:
        """ spacing area """
        HEIGHT = 20
        BACKGROUND_COLOR = "grey"

    class Buttons:
        """ preset buttons """
        # layout
        NUM_BUTTONS_PER_ROW = 2
        BUTTON_HEIGHT = 80

        FONT = ("Helvetica", 24)

        BACKGROUND_COLOR = "cornflower blue"
        TEXT_COLOR = "black"


