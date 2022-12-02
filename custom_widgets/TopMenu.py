from tkinter import Menu
from custom_widgets.ShortcutScreen import open_shortcut_list
from functools import partial


class TopMenu(Menu):
    def __init__(self, root, code_editor):
        Menu.__init__(self, root)

        # File menu commands
        file_menu = Menu(self, tearoff=0)
        file_menu.add_command(label="New File", command=code_editor.add_tab)
        file_menu.add_command(label="Open File", command=code_editor.open_file)
        file_menu.add_command(label="Save", command=code_editor.save_file)
        file_menu.add_command(label="Save as", command=code_editor.save_file_as)
        self.add_cascade(label="File", menu=file_menu)

        # Compile code menu commands
        compile_menu = Menu(self, tearoff=0)
        compile_menu.add_command(label="Compile Code", command=code_editor.compile_file)
        compile_menu.add_command(label="Show Tokenized Code", command=code_editor.show_tokenized_code)
        self.add_cascade(label="Compile", menu=compile_menu)

        # Execute code menu commands
        execute_menu = Menu(self, tearoff=0)
        execute_menu.add_command(label="Run/Execute Code")
        execute_menu.add_command(label="Compile and Run Code")
        self.add_cascade(label="Execute", menu=execute_menu)

        # Help menu commands
        help_menu = Menu(self, tearoff=0)
        help_menu.add_command(label="Show shortcuts", command=partial(open_shortcut_list, code_editor))
        self.add_cascade(label="Help", menu=help_menu)
