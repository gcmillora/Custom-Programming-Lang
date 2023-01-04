from tkinter import LabelFrame, Text, Scrollbar
from math import ceil, floor


# Console/Terminal frame that contains status, compile, and runtime execution display
class Console(LabelFrame):
    def __init__(self, parent, color_config):
        # Set window size based on parent widget size
        self._window_config = (int(parent.winfo_reqwidth() * 0.8),
                               int(parent.winfo_reqheight() * 0.17))

        self.color_config = color_config

        LabelFrame.__init__(self,
                            master=parent,
                            text="Console",
                            background=self.color_config["alt_bg"],
                            foreground=self.color_config["fg"])
        self.grid(column=0, row=1, sticky="nsew")
        self.grid_propagate(False)  # Locks the size of the frame to set width and height
        self.update_idletasks()  # Make sure the info about the frame is updated

        self._text_config = (floor((190 * self.winfo_reqwidth()) / 1230),
                             ceil((14 * self.winfo_reqheight()) / 147))

        self.console_area = Text(self,
                                 state="disabled",
                                 width=self._text_config[0],
                                 height=self._text_config[1],
                                 background=self.color_config["alt_bg"],
                                 foreground=self.color_config["fg"],
                                 insertbackground=self.color_config["fg"],
                                 wrap="word")
        self.console_area.pack(side="left", fill="both", expand=True)
        # Set the color of errors in the console to red
        self.console_area.tag_config("error", foreground="red")
        self.console_area.tag_config("success", foreground="green")

        # Set the scroll bar for the console/terminal
        self.scrollbar = Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.console_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.console_area.yview)

    # Triggered when specific variables are changed in the StateManager
    # Specifically, this method handles any text to be displayed in the console
    def notify(self, states):
        # Trigger to clear the console
        if states.to_clear_console:
            # Clear all text in the console
            self.console_area.config(state="normal")
            self.console_area.delete(1.0, 'end')
            self.console_area.config(state="disabled")

        # states.console_display is the temporary storage for any text to be displayed in the console
        if states.console_display is None:  # If the console_display is empty then skip
            return

        self.console_print(states.console_display)
        states.console_display = None  # Return console_display to NoneType

    # Writes the status and results to the text widget
    def console_print(self, text: str | list[str]):
        # Temporarily removes the disabled state to allow text to be inserted
        self.console_area.config(state="normal")

        # Check if the text is string
        if type(text) is str:
            # Check if the text to be display is an error or info
            # If it is an error change the text color to red
            format_text = text.split("<>")
            log_type = format_text[0]
            user_text = ''.join(format_text[1:])
            self.console_area.insert("end", f"{log_type}", log_type.lower())
            self.console_area.insert("end", f": {user_text}\n")
        else:
            # If the text is a list of strings then write them one by one to the text widget
            for line in text:
                format_text = line.split("<>")
                log_type = format_text[0]
                user_text = ''.join(format_text[1:])
                self.console_area.insert("end", f"{log_type}", log_type.lower())
                self.console_area.insert("end", f": {user_text}\n")

        # Return the state to disabled to disallow the user to modify the console log
        self.console_area.config(state="disabled")
