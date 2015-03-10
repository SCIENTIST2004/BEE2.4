from tkinter import messagebox

import traceback
import time

from BEE2_config import GEN_OPTS

from tk_root import TK_ROOT
import UI
import loadScreen
import paletteLoader
import packageLoader
import gameMan

ERR_FORMAT = '''
--------------

{time!s}
{underline}
{exception!s}
'''

loadScreen.length('UI', 9)

DEFAULT_SETTINGS = {
    'Directories': {
        'palette': 'palettes\\',
        'package': 'packages\\',
        },
    'General': {
        'preserve_BEE2_resource_dir': '0',
        'allow_any_folder_as_game': '0',
        'mute_sounds': '0',
        'debug_mode': '0',
        },
    }

DEBUG_MODE = False

try:

    UI.load_settings(GEN_OPTS)

    DEBUG_MODE = GEN_OPTS.get_bool('General', 'debug_mode')

    # If we have no games, gameMan will quit the app entirely.
    gameMan.load(UI.quit_application, loadScreen.win)

    gameMan.set_game_by_name(
        GEN_OPTS.get_val('Last_Selected', 'Game', ''),
        )

    print('Loading Packages...')
    UI.load_packages(
        packageLoader.load_packages(
            GEN_OPTS['Directories']['package'],
            not GEN_OPTS.get_bool('General', 'preserve_BEE2_resource_dir'),
            )
        )
    print('Done!')

    print('Loading Palettes...')
    UI.load_palette(
        paletteLoader.load_palettes(GEN_OPTS['Directories']['palette']),
        )
    print('Done!')

    print('Initialising UI...')
    UI.init_windows()  # create all windows
    print('Done!')

    loadScreen.close_window()
    UI.event_loop()

except Exception as e:
    # Grab Python's traceback, and record it
    # This way we have a log.
    loadScreen.close_window()

    err = traceback.format_exc()
    if DEBUG_MODE:
        # Put it onscreen
        messagebox.showinfo(
            title='BEE2 Error!',
            message=str(e).strip('".')+'!',
            icon=messagebox.ERROR,
            parent=TK_ROOT,
            )

    # Weekday Date Month Year HH:MM:SS AM/PM
    cur_time = time.strftime('%A %d %B %Y %I:%M:%S%p') + ':'

    print('Logging ' + repr(e) + '!')

    # Always log the exception into a file.
    with open('BEE2-error.log', 'a') as log:
        log.write(ERR_FORMAT.format(
            time=cur_time,
            underline='='*len(cur_time),
            exception=err,
        ))
    # We still want to crash!
    raise