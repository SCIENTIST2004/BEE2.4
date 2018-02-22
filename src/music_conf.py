"""Handles the music configuration UI."""
from typing import Dict, Iterable, Optional, List

from BEE2_config import GEN_OPTS
from SubPane import SubPane
from loadScreen import LoadScreen
from packageLoader import Music, MusicChannel, Style
import tkinter
import utils
from tkinter import ttk
from selectorWin import Item as SelItem, selWin as SelectorWin, AttrDef as SelAttr
from srctools import FileSystemChain, FileSystem
from tk_tools import TK_ROOT

BTN_EXPAND = '▽'
BTN_EXPAND_HOVER = '▼'
BTN_CONTRACT = '△'
BTN_CONTRACT_HOVER = '▲'

LOGGER = utils.getLogger(__name__)

WINDOWS = {}  # type: Dict[MusicChannel, SelectorWin]
SEL_ITEMS = {}  # type: Dict[str, SelItem]

is_collapsed = False

filesystem = FileSystemChain()


def load_filesystems(systems: Iterable[FileSystem]):
    """Record the filesystems used for each package, so we can sample sounds."""
    for system in systems:
        filesystem.add_sys(system, prefix='resources/music_samp/')


def set_suggested(music_id: str):
    """Set the music ID that is suggested for the base."""
    music = Music.by_id(music_id)
    for channel in MusicChannel:
        WINDOWS[channel].set_suggested(music.get_suggestion(channel))


def selwin_callback(music_id: Optional[str], channel: MusicChannel):
    """Callback for the selector windows.

    This saves into the config file the last selected item.
    """
    if music_id is None:
        music_id = '<NONE>'
    GEN_OPTS['Last_Selected']['music_' + channel.name.casefold()] = music_id


def load_selitems(loader: LoadScreen):
    """Load the selector items early, to correspond with the loadscreen order."""
    for item in Music.all():
        sel_item = SEL_ITEMS[item.id] = SelItem.from_data(
            item.id,
            item.selitem_data,
            item.get_attrs()
        )
        sel_item.snd_sample = item.sample
        loader.step('IMG')


def make_widgets(frame: ttk.LabelFrame, pane: SubPane) -> SelectorWin:
    """Generate the UI components, and return the base window."""

    def for_channel(channel):
        """Get the items needed for a specific channel."""
        return [
            SEL_ITEMS[music.id].copy()
            for music in Music.all()
            if music.provides_channel(channel)
        ]

    base_win = WINDOWS[MusicChannel.BASE] = SelectorWin(
        TK_ROOT,
        for_channel(MusicChannel.BASE),
        title=_('Select Background Music - Base'),
        desc=_('This controls the background music used for a map. Some '
               'tracks have variations which are played when interacting '
               'with certain testing elements.'),
        has_none=True,
        sound_sys=filesystem,
        none_desc=_('Add no music to the map at all.'),
        callback=selwin_callback,
        callback_params=[MusicChannel.BASE],
        attributes=[
            SelAttr.bool('SPEED', _('Propulsion Gel SFX')),
            SelAttr.bool('BOUNCE', _('Repulsion Gel SFX')),
            SelAttr.bool('TBEAM', _('Excursion Funnel Music')),
            SelAttr.bool('TBEAM_SYNC', _('Synced Funnel Music')),
        ],
    )

    WINDOWS[MusicChannel.TBEAM] = SelectorWin(
        TK_ROOT,
        for_channel(MusicChannel.TBEAM),
        title=_('Select Excursion Funnel Music'),
        desc=_('This controls the background music used for a map. Some '
               'tracks have variations which are played when interacting '
               'with certain testing elements.'),
        has_none=True,
        sound_sys=filesystem,
        none_desc=_('Have no music playing when inside funnels.'),
        callback=selwin_callback,
        callback_params=[MusicChannel.TBEAM],
        attributes=[
            SelAttr.bool('TBEAM_SYNC', _('Synced Funnel Music')),
        ],
    )

    WINDOWS[MusicChannel.BOUNCE] = SelectorWin(
        TK_ROOT,
        for_channel(MusicChannel.BOUNCE),
        title=_('Select Repulsion Gel Music'),
        desc=_('Select the music played when players jump on Repulsion Gel.'),
        has_none=True,
        sound_sys=filesystem,
        none_desc=_('Add no music when jumping on Repulsion Gel.'),
        callback=selwin_callback,
        callback_params=[MusicChannel.BOUNCE],
    )

    WINDOWS[MusicChannel.SPEED] = SelectorWin(
        TK_ROOT,
        for_channel(MusicChannel.SPEED),
        title=_('Select Propulsion Gel Music'),
        desc=_('Select music played when players have large amounts of horizontal velocity.'),
        has_none=True,
        sound_sys=filesystem,
        none_desc=_('Add no music while running fast.'),
        callback=selwin_callback,
        callback_params=[MusicChannel.SPEED],
    )

    assert set(WINDOWS.keys()) == set(MusicChannel), "Extra channels?"

    # Widgets we want to remove when collapsing.
    exp_widgets = []  # type: List[tkinter.Widget]

    def toggle_btn_enter(event=None):
        toggle_btn['text'] = BTN_EXPAND_HOVER if is_collapsed else BTN_CONTRACT_HOVER

    def toggle_btn_exit(event=None):
        toggle_btn['text'] = BTN_EXPAND if is_collapsed else BTN_CONTRACT

    def set_collapsed():
        """Configure for the collapsed state."""
        global is_collapsed
        is_collapsed = True
        GEN_OPTS['Last_Selected']['music_collapsed'] = '0'
        base_lbl['text'] = _('Music: ')
        toggle_btn_exit()
        for wid in exp_widgets:
            wid.grid_remove()

    def set_expanded():
        """Configure for the expanded state."""
        global is_collapsed
        is_collapsed = False
        GEN_OPTS['Last_Selected']['music_collapsed'] = '1'
        base_lbl['text'] = _('Base: ')
        toggle_btn_exit()
        for wid in exp_widgets:
            wid.grid()
        pane.update_idletasks()
        pane.move()

    def toggle(event=None):
        if is_collapsed:
            set_expanded()
        else:
            set_collapsed()
        pane.update_idletasks()
        pane.move()

    frame.columnconfigure(2, weight=1)

    base_lbl = ttk.Label(frame)
    base_lbl.grid(row=0, column=1)

    toggle_btn = ttk.Label(frame, text=' ')
    toggle_btn.bind('<Enter>', toggle_btn_enter)
    toggle_btn.bind('<Leave>', toggle_btn_exit)
    toggle_btn.bind('<ButtonPress-1>', toggle)
    toggle_btn.grid(row=0, column=0)

    for row, channel in enumerate(MusicChannel):
        btn = WINDOWS[channel].widget(frame)
        if row:
            exp_widgets.append(btn)
        btn.grid(row=row, column=2, sticky='EW')

    for row, text in enumerate([
        _('Funnel:'),
        _('Bounce:'),
        _('Speed:'),
    ], start=1):
        label = ttk.Label(frame, text=text)
        exp_widgets.append(label)
        label.grid(row=row, column=1, sticky='EW')

    if GEN_OPTS.get_bool('Last_Selected', 'music_collapsed', True):
        set_collapsed()
    else:
        set_expanded()

    return base_win


def selected_ids():
    return None


def is_suggested():
    return None