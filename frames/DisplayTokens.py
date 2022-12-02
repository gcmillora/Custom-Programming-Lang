from tkinter import Toplevel, Scrollbar
from tkinter.ttk import Treeview


class DisplayTokens(Toplevel):
    def __init__(self, root, token_list: list[tuple[str, str, str]]):
        Toplevel.__init__(self, root)
        self.geometry("500x502")
        self.title("Token List")

        TokenList(self, token_list)
        self.protocol("WM_DELETE_WINDOW", self.destroy)


class TokenList(Treeview):
    def __init__(self, parent: DisplayTokens, token_list: list[tuple[str, str, str]]):
        Treeview.__init__(self,
                          parent,
                          columns=("name", "type", "line"),
                          height=len(token_list))
        self.tag_configure("oddrow", background="#ced4da")

        self.column("#0", width=0, stretch=False)
        self.column("name", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))
        self.column("type", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))
        self.column("line", anchor="center", width=int(parent.winfo_reqwidth() * 0.5))

        self.heading("#0", text="", anchor="center")
        self.heading("name", text="NAME", anchor="center")
        self.heading("type", text="TYPE", anchor="center")
        self.heading("line", text="LINE", anchor="center")

        for idx, token in enumerate(token_list):
            # Set table insert options
            options = {
                "parent": "",
                "index": "end",
            }

            if idx % 2 != 0:
                options["tags"] = "oddrow"
            self.insert(**options, values=(token[0], token[1], token[2]))

        self.__scrollbar = Scrollbar(self, orient="vertical")
        self.config(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.config(command=self.yview)

        self.__scrollbar.pack(side="right", fill="y")
        self.pack(side="right", fill="both", expand=True)
