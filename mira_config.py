
"""
Minimalist Internet Radio - config settings
"""

class MiraConfig:
    """ config settings """

    class General:
        MPC_PATH = "/usr/bin/mpc"
        SAVED_STATE_FILENAME = "mira_state.json"

    class Display:
        """ display properties """
        WIDTH = 800
        HEIGHT = 480

    class Title:
        USE_24h_TIME_FORMAT = True
        BACKGROUND_COLOR = "lightblue"
        UPDATE_INTERVAL = 5000

    class Status:
        """ status pane """
        FONT = ("Helvetica", 16)

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

        FONT = ("Helvetica", 16)

        BACKGROUND_COLOR = "red"
        TEXT_COLOR = "black"


