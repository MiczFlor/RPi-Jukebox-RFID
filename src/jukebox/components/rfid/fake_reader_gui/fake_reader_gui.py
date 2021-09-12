# MIT License
#
# Copyright (c) 2021 Micz Flor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Christian Banz
# - arne123
#
"""
A fake reader using a TK GUI for development purposes

When using Anaconda, the GUI will look horrible!
That is because Anaconda's TK is compiled without FreeType support

The very quick and very dirty fix:
Replacing the tk lib in anacondas environment with the system libtk.
cd /path/to/anaconda3/envs/rpi/lib
mv ./libtk8.6.so ./libtk8.6.so.bak
ln -s /usr/lib/x86_64-linux-gnu/libtk8.6.so libtk8.6.so

Reference:
https://stackoverflow.com/questions/47769187/make-anacondas-tkinter-aware-of-system-fonts-or-install-new-fonts-for-anaconda
"""
import os
import signal
import functools
import logging
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ttkthemes import ThemedStyle

from components.rfid import ReaderBaseClass
from components.rfid.cardutils import (card_to_str)
import jukebox.cfghandler

from .description import DESCRIPTION

# Create logger
logger = logging.getLogger('jb.rfid.tk')
cfg = jukebox.cfghandler.get_handler('rfid')
cfg_cards = jukebox.cfghandler.get_handler('cards')


def query_customization() -> dict:
    print("\nThere are a few graphical customization options. Please edit YAML file directly.")
    return {'default_padx': 20,
            'default_pady': 20,
            'default_btn_width': 15,
            'raise_window': True,
            'window_position': '-150+50'}


def gui_close():
    logger.info("TKinter GUI close requested")
    # We will just raise a Ctrl-C Interrupt with the main thread for now
    # There is now "close-down" by remote-thread call implemented at the moment
    os.kill(os.getpid(), signal.SIGINT)


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key):
        self._logger = logging.getLogger(f'jb.rfid.tk({reader_cfg_key})')
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)
        self._cancel = threading.Event()

        config = cfg.getn('rfid', 'readers', reader_cfg_key, 'config', default={})
        with cfg:
            default_padx = config.setdefault('default_padx', default=20)
            default_pady = config.setdefault('default_pady', default=20)
            default_btn_width = config.setdefault('default_btn_width', default=15)
            default_raise_win = config.setdefault('raise_window', default=True)
            default_window_position = config.get('window_position', None)

        # Create the UI
        # ttkthemes (With explicit access to the style)
        # https://www.codespeedy.com/changing-theme-of-a-tkinter-gui/
        self._window = tk.Tk()
        self._style = ThemedStyle(self._window)
        self._style.set_theme('yaru')
        self._window.config(bg='gray96')
        # Further customization
        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-style-layer.html
        # self._style.configure("my.TMenubutton", foreground="black", background="black")
        #
        # Note about ttkbootstrap: This does not exit the application properly when started in this reader thread

        if default_window_position is not None:
            self._window.geometry(default_window_position)
        print(f"{self._window.geometry()}")

        self._window.title('RFID Reader Simulator')
        # Create three stacked Frames for RFID, Trigger, Place
        self._lframe0 = ttk.Labelframe(self._window, text='Card database')
        self._lframe0.grid(column=0, row=0, padx=default_padx, pady=default_pady, sticky='EW')
        self._lframe1 = ttk.Labelframe(self._window, text='RFID Card Selection')
        self._lframe1.grid(column=0, row=1, padx=default_padx, pady=default_pady, sticky='EW')
        self._lframe2 = ttk.Labelframe(self._window, text='USB Reader (Single place action)')
        self._lframe2.grid(column=0, row=2, padx=default_padx, pady=default_pady, sticky='EW')
        self._lframe3 = ttk.Labelframe(self._window, text='RDM6300 / RC522 (Permanent place)')
        self._lframe3.grid(column=0, row=3, padx=default_padx, pady=default_pady, sticky='EW')

        # Frame 0
        self._database_file = f"{jukebox.cfghandler.get_handler('jukebox').getn('rfid', 'card_database')}"
        self._database_label = ttk.Label(self._lframe0, text=f"{self._database_file}", padding=0)
        self._database_label.pack(side='top', padx=default_padx, pady=default_pady, anchor='w')
        # self._btn_database = ttk.Button(self._lframe0, text="Change", width=default_btn_width,
        #                                 command=self._btn_database_callback)
        # self._btn_database.pack(side='top', padx=default_padx, pady=default_pady, anchor='w')

        # Frame 1
        card_ids = cfg_cards.keys()
        try:
            card_id_init = card_ids.__iter__().__next__()
        except StopIteration:
            card_id_init = ""
        self._menu_rfid_value = tk.StringVar()

        # Using Menubutton to separate value and show different label
        # https://www.pythontutorial.net/tkinter/tkinter-menubutton/
        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-Menubutton.html
        self._menu_var = tk.StringVar()
        self._menu_var.trace('w', self._menu_rfid_callback2)
        self._menu_btn = ttk.Menubutton(self._lframe1, text='Select RFID Card')
        self._menu = tk.Menu(self._menu_btn, tearoff=0,
                             background='gray96', relief=tk.FLAT,
                             activeborderwidth=0, borderwidth=0)
        id_max_len = max(4, functools.reduce(lambda x, y: max(x, len(y)), card_ids, 0))
        for c in card_ids:
            self._menu.add_radiobutton(value=c, label=f"{c:>{id_max_len}}: {card_to_str(c)}",
                                       variable=self._menu_var,
                                       font='TkFixedFont')
        self._menu.add_radiobutton(value='DEAD', label=f"{'DEAD':>{id_max_len}}: Unknown Card ID",
                                   variable=self._menu_var,
                                   font='TkFixedFont')
        # In case you need to check what font 'TkFixedFont' is mapped to, use these two lines
        # from tkinter import font
        # print(f'{font.nametofont("TkFixedFont").actual()}')
        self._menu_btn['menu'] = self._menu
        self._menu_btn.pack(side='top', padx=default_padx, pady=default_pady, fill='x')

        self._lab_card_id = ttk.Label(self._lframe1, text='Card: No card selected', padding=0)
        self._lab_card_id.pack(side='top', padx=default_padx + 1, pady=0, fill='x')

        self._cbtn_action_status = tk.StringVar()
        self._cbtn_action = ttk.Checkbutton(self._lframe1, text='  Selection triggers card read-out',
                                            variable=self._cbtn_action_status,
                                            command=self._cbtn_action_callback)
        self._cbtn_action.pack(side='left', padx=default_padx, pady=default_pady)

        # Frame 2
        self._btn_trigger = ttk.Button(self._lframe2, text="Trigger card", width=default_btn_width,
                                       command=self._btn_trigger_callback)
        self._btn_trigger.pack(side='left', padx=default_padx, pady=default_pady)

        # Frame 3
        self._if3_1 = ttk.Frame(self._lframe3)
        self._if3_1.pack(side='top', fill='x')
        self._if3_2 = ttk.Frame(self._lframe3)
        self._if3_2.pack(side='bottom', fill='x')

        self._btn_place = ttk.Button(self._if3_1, text="Place card", width=default_btn_width,
                                     command=self._btn_place_callback)
        self._btn_place.pack(side='left', padx=default_padx, pady=default_pady, fill='x')

        self._btn_remove = ttk.Button(self._if3_1, text="Remove card", width=default_btn_width,
                                      command=self._btn_remove_callback)
        self._btn_remove.pack(side='left', padx=default_padx, pady=default_pady, fill='x')
        self._lab_card_place = ttk.Label(self._if3_2, text='No card on reader', padding=0)
        self._lab_card_place.pack(side='top', padx=default_padx, pady=default_pady, fill='x')

        self._window.protocol("WM_DELETE_WINDOW", gui_close)

        # Set initial status
        self._card_id_prev = card_id_init
        self._card_id = card_id_init
        self._in_waiting = True
        self._card_on_reader = False
        self._trigger_action = False
        self._btn_remove_callback()
        self._cbtn_action_status.set(0)
        # Setting the menu_var triggers the callback self._menu_rfid_callback2()
        self._menu_var.set(self._card_id)

        if default_raise_win:
            self._window.tkraise()
        else:
            self._window.lower()

    def _btn_database_callback(self):
        new_file = filedialog.askopenfilename(initialdir=".", title="Select file",
                                                         filetypes=(("YAML files", "*.yaml"), ("all files", "*.*")))
        if new_file != '':
            self._database_file = new_file
            print(f"{self._database_file}")
            self._database_label['text'] = self._database_file

    def _cbtn_action_callback(self):
        # logger.debug(f"Checkbutton = {self._cbtn_action_status.get()}")
        # self._trigger_action = True
        pass

    def _menu_rfid_callback2(self, *args):
        self._card_id = self._menu_var.get()
        readable = card_to_str(self._card_id, long=True, multiline=True)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Selected card command: {card_to_str(self._card_id, long=True, multiline=False)}")
        self._lab_card_id['text'] = f"ID: '{self._menu_var.get()}'\n{readable}"

    def _btn_trigger_callback(self):
        self._trigger_action = True

    def _btn_place_callback(self):
        self._btn_place['state'] = tk.DISABLED
        self._btn_trigger['state'] = tk.DISABLED
        self._btn_remove['state'] = tk.NORMAL
        self._lab_card_place['text'] = 'Card placed on reader'
        self._card_on_reader = True

    def _btn_remove_callback(self):
        self._btn_remove['state'] = tk.DISABLED
        self._btn_trigger['state'] = tk.NORMAL
        self._btn_place['state'] = tk.NORMAL
        self._lab_card_place['text'] = 'No card on reader'
        self._card_on_reader = False

    def cleanup(self):
        logger.debug("Destroy")
        # There is no need to call self._window.destroy()
        # this will happen implicitly when thread ends!

    def stop(self):
        logger.debug("Stopping")
        self._cancel.set()

    def read_card(self) -> str:
        # Need to embed this into the reader loop structure, so cannot use self._window.mainloop()
        while not self._cancel.is_set():
            self._window.update()

            if self._card_on_reader:
                break
            else:
                if self._trigger_action:
                    break
                elif self._cbtn_action_status.get() != '0' and self._card_id != self._card_id_prev:
                    break

            self._cancel.wait(timeout=0.1)

        # Always clear trigger status to prevent transient errors
        self._trigger_action = False

        if self._cancel.is_set():
            logger.debug("Empty return")
            return ''
        else:
            logger.debug(f"Returning ID {self._card_id}")
            self._card_id_prev = self._card_id
            return self._card_id
