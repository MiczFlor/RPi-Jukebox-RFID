import tkinter as tk
import time


class FakeReader:
    def __init__(self):
        self._keep_running = True
        self.root = None
        self.card_id = None
        self.card_id_prev = None

    def create_ui(self):
        self.root = tk.Tk()
        self.root.title("Fake RFID Reader")
        self.root.geometry("200x100")
        self.root.geometry("-120+50")

        # Add a grid
        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.pack(pady=20, padx=1)

        # Create a Tkinter variable
        self.tkvar = tk.StringVar(self.root)

        popupMenu = tk.OptionMenu(self.mainframe, self.tkvar, *self.card_ids)
        tk.Label(self.mainframe, text="Choose a RFID Card Number").grid(row=1, column=1)
        popupMenu.grid(row=2, column=1)

        # link function to change dropdown
        self.tkvar.trace('w', self.change_dropdown)

        self.root.lower()

    # on change dropdown value
    def change_dropdown(self, *args):
        self.card_id = self.tkvar.get()

    def set_card_ids(self, card_ids):
        self.card_ids = card_ids

    def readCard(self):
        if self.root is None:
            self.create_ui()

        while self.card_id == self.card_id_prev:
            if self.root is not None:
                self.root.update()
                time.sleep(0.1)

        self.card_id_prev = self.card_id

        return self.card_id
