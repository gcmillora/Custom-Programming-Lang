from tkinter import Toplevel, Scrollbar
from tkinter.ttk import Treeview
from utils.Utils import get_shortcuts


class ShortcutScreen(Toplevel):
    def __init__(self, root):
        Toplevel.__init__(self, root)
        self.geometry("750x200")
        self.title("Shortcut Keys")

        ShortcutList(self, get_shortcuts())
        self.protocol("WM_DELETE_WINDOW", self.destroy)


class ShortcutList(Treeview):
    def __init__(self, parent: ShortcutScreen, key_bindings: dict):
        Treeview.__init__(self,
                          parent,
                          columns=("action", "key", "description"),
                          height=len(key_bindings))
        self.tag_configure("oddrow", background="#ced4da")

        self.column("#0", width=0, stretch=False)
        self.column("action", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))
        self.column("key", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))
        self.column("action", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))

        self.heading("#0", text="", anchor="center")
        self.heading("action", text="ACTION", anchor="center")
        self.heading("key", text="KEY BINDING", anchor="center")
        self.heading("description", text="DESCRIPTION", anchor="center")

        for idx, action in enumerate(key_bindings):
            # Set table insert options
            options = {
                "parent": "",
                "index": "end",
            }

            if idx % 2 != 0:
                options["tags"] = "oddrow"
            self.insert(**options, values=(action, key_bindings[action]["key"], key_bindings[action]["desc"]))

        self.__scrollbar = Scrollbar(self, orient="vertical")
        self.config(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.config(command=self.yview)

        self.__scrollbar.pack(side="right", fill="y")
        self.pack(side="right", fill="both", expand=True)


def open_shortcut_list(root):
    ShortcutScreen(root)
