from tkinter import Tk, Menu
from sys import platform
from frames.CodeEditor import CodeEditor
from frames.Console import Console
from frames.VarTable import VarTable
from utils.StateManager import StateManager

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
    code_editor = CodeEditor(root, states)
    console = Console(root)
    var_table = VarTable(root)

    # Adds frames as observers, and they will be notified if specific values of variables changed
    states.subscribe(var_table)
    states.subscribe(console)

    menubar = Menu(root)

    # File menu commands
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label="New File", command=code_editor.add_tab)
    file_menu.add_command(label="Open File", command=code_editor.open_file)
    file_menu.add_command(label="Save", command=code_editor.save_file)
    file_menu.add_command(label="Save as", command=code_editor.save_file_as)
    menubar.add_cascade(label="File", menu=file_menu)

    # Compile code menu commands
    compile_menu = Menu(menubar, tearoff=0)
    compile_menu.add_command(label="Compile Code", command=code_editor.compile_file)
    compile_menu.add_command(label="Run/Execute Code")
    compile_menu.add_command(label="Compile and Run Code")
    compile_menu.add_command(label="Show Tokenized Code")
    menubar.add_cascade(label="Code", menu=compile_menu)

    # Run the window
    root.config(menu=menubar, background="#263238")
    root.mainloop()
