from tkinter import LabelFrame, Scrollbar, Canvas
from tkinter.ttk import Treeview


# Frame that contains the list of variables of the IOL
class VarTableContainer(LabelFrame):
    def __init__(self, parent):
        # Set window size based on parent widget size
        self._window_config = (int(parent.winfo_width() * 0.19),
                               int((1006 * parent.winfo_height()) / 1048))

        LabelFrame.__init__(self,
                            master=parent,
                            width=self._window_config[0],
                            height=self._window_config[1],
                            text="Variable Table")
        self.grid(column=1, row=0, rowspan=2, sticky="nsew")
        self.grid_propagate(False)  # Locks the size of the frame to set width and height

        self.wrapper = VarTable(self)

    # Triggered when specific variables are changed in the StateManager
    # Specifically, this method handles any variable to be displayed in the table
    def notify(self, states):
        try:
            # states.current_tab is the index of the current tab in focus
            if states.current_tab is None:  # If the console_display is empty then skip
                self.wrapper.clear_table()  # Clear the table for any values
                return
            variables = states.var_tables[states.current_tab]
            self.wrapper.update_table(variables)

        except IndexError:
            # Append an empty list to store the list of variables for the code editor tab
            states.var_tables.append([])


class VarTable(Canvas):
    def __init__(self, parent: VarTableContainer):
        Canvas.__init__(self,
                        parent,
                        height=int(parent.winfo_reqheight() / 21.5),
                        width=parent.winfo_reqwidth() - 20)

        # Initializes the table widget that contains the variables used by the IOL
        self.__var_table = Treeview(self,
                                    columns=("name", "line"),
                                    height=self.winfo_reqheight())
        self.__var_table.tag_configure("oddrow", background="#ced4da")

        # Removes empty column that is default in every Treeview
        self.__var_table.column("#0", width=0, stretch=False)
        self.__var_table.column("name", anchor="w", width=int(self.winfo_reqwidth() * 0.5))
        self.__var_table.column("line", anchor="center", width=int(self.winfo_reqwidth() * 0.5))

        self.__var_table.heading("#0", text="", anchor="center")
        self.__var_table.heading("name", text="ID", anchor="center")
        self.__var_table.heading("line", text="LINE", anchor="center")

        self.__scrollbar = Scrollbar(self, orient="vertical")
        self.__var_table.config(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.config(command=self.__var_table.yview)

        self.__var_table.grid(column=0, row=0, sticky="nsew")
        self.__scrollbar.grid(column=1, row=0, sticky="ns")

        self.pack(side="left", fill="both")
        self.pack_propagate(False)

    def clear_table(self):
        self.__var_table.delete(*self.__var_table.get_children())

    def update_table(self, variables: list):
        try:
            # Clear the table before inserting new values
            self.clear_table()

            for idx, variable in enumerate(variables):
                # Set table insert options
                options = {
                    "parent": "",
                    "index": "end",
                }

                # Set the color of the odd numbered rows to gray
                if (idx % 2) != 0:
                    options["tags"] = "oddrow"
                self.__var_table.insert(**options, values=(variable[0], variable[2]))
            self.__var_table.grid(column=0, row=0)
        except ValueError:
            raise
