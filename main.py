from tkinter import Tk
from sys import platform
from frames.CodeEditorNotebook import CodeEditorNotebook
from frames.Console import Console
from frames.VarTableContainer import VarTableContainer
from utils.StateManager import StateManager
from custom_widgets.TopMenu import TopMenu

if __name__ == '__main__':
    # Window config
    root = Tk()
    root.title("FLOPOL Program")

    # Setting window to zoomed is platform dependent
    if platform == "linux" or platform == "linux2":
        root.attributes("-zoomed", True)
    else:
        root.state("zoomed")

    root.update_idletasks()

    # Instantiate State Manager to store global variables
    states = StateManager()

    # Instantiate main frames
    code_editor = CodeEditorNotebook(root, states)
    console = Console(root, states.color_config)
    var_table = VarTableContainer(root)

    # Adds frames as observers, and they will be notified if specific values of variables changed
    states.subscribe(var_table)
    states.subscribe(console)

    # Set menu on top of screen
    menubar = TopMenu(root, code_editor)

    # Run the window
    root.config(menu=menubar, background="#263238")
    root.mainloop()
