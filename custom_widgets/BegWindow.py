from tkinter import Toplevel, Frame, Label, Entry, Button


# Custom fr
class BegWindow(Toplevel):
    def __init__(self, parent, update_input, label):
        Toplevel.__init__(self, parent)
        self.title("Value Input")
        self.update_input = update_input

        self.wrapper = Frame(self)
        self.wrapper.pack(padx=5, pady=5)
        Label(self.wrapper, text=label).grid(row=0, columnspan=2)

        self.__text_input = Entry(self.wrapper, width=50)
        self.__text_input.grid(row=1, column=0)

        Button(self.wrapper,
               text="SUBMIT",
               command=self.update_cache).grid(row=1, column=1, sticky="e")

        self.bind("<Return>", self.update_cache)

        # Properly delete window from memory
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # Update the current cached value
    def update_cache(self, *_):
        input_val = self.__text_input.get()
        self.deiconify()
        self.destroy()
        self.update()
        self.update_input(input_val)
