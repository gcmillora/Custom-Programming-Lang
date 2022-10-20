from tkinter import Frame, Text, Scrollbar, TclError, Menu, filedialog
from tkinter.ttk import Notebook
from utils.StateManager import StateManager
from utils.Utils import open_filedialog, open_file_prompt, write_to_file, compile_file, is_iol_valid, print_to_console
from utils.CustomErrors import InvalidIOLFileError, InvalidLexemeError, EmptyFileReturnError


# Notebook that contains all tabs for the code editor
class CodeEditor(Notebook):
    def __init__(self, parent, states: StateManager):
        # Used to modify values in the state manager
        self.states = states
        self._parent_window_size = (int(parent.winfo_width() * 0.81),
                                    int(parent.winfo_height() * 0.7))

        Notebook.__init__(self,
                          master=parent,
                          width=self._parent_window_size[0],
                          height=self._parent_window_size[1])

        # Calls change_tab() method when the user changes tabs
        self.bind("<<NotebookTabChanged>>", self.change_tab)

        # Shortcut bindings for menu options
        parent.bind("<Control-p>", self.compile_file)
        parent.bind("<Control-s>", self.save_file)
        parent.bind("<Control-Shift-s>", self.save_file_as)

        self.grid(column=0, row=0, sticky="nw")
        self.grid_propagate(False)

        # Initializes right-click menu for closing the current tab
        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Close current tab", command=self.close_tab)
        self.bind("<Button-3>", self.open_popup)

        self.color_config = {
            "bg": "#37474F",
            "fg": "#ECEFF1"
        }

        # Stores instances of the text widgets of each tab
        self.textbox_list: list[CodeEditorTextBox] = []

        # Creates a new empty tab by default
        self.add_tab()

    def get_screen_size(self):
        return self.winfo_reqwidth(), self.winfo_reqheight()

    # Opens the right-click menu
    def open_popup(self, event):
        try:
            self.right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()

    # Adds a new code editor tab
    def add_tab(self, name="New File"):
        try:
            # Check if the name is assigned
            if name == "New File":
                idx = self.index('end') if self.index('end') > 0 else ""
                name = f"*{name} {idx}"

            textbox = CodeEditorTextBox(self)
            self.textbox_list.append(textbox)

            # Create a new tab with the new textbox instance
            self.add(textbox, text=name)

            # Creates a new entry for var table in the state manager
            self.states.init_var_table()

            return textbox
        except TclError:
            self.states.console_display = print_to_console("Error in adding new tab", "error")

    # Close the current tab
    def close_tab(self):
        # Remove the instance from the textbox list
        self.textbox_list.pop(self.states.current_tab)

        # Remove the states attached to the current tab
        self.states.remove_tab()
        self.forget("current")

    # Updates the index stored in the state manager
    def change_tab(self, event, *args):
        try:
            self.states.current_tab = self.index(event.widget.select())
        except TclError:
            # If there are no tabs open then set current tab to NoneType
            self.states.current_tab = None

    # Rename the current tab (used when opening existing IOL files)
    def rename_tab(self, new_name: str):
        self.tab("current", text=new_name)

    # Open existing IOL file
    def open_file(self):
        try:
            # Get the content and path of the file as a tuple
            dialog_res = open_filedialog()
            filename = dialog_res[1].split("/")[-1]

            # If there are no tabs open create a new tab
            if self.states.current_tab is None:
                curr_textbox: CodeEditorTextBox = self.add_tab(filename)
            else:
                curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

                # If the current textbox is not empty, ask the user if the file should be opened in a new tab
                if len(curr_textbox.textarea.get(1.0, "end")) - 1 > 0 and open_file_prompt():
                    curr_textbox = self.add_tab(filename)
                else:
                    self.rename_tab(filename)

            # Write the content of the file to the textbox
            curr_textbox.handle_text_on_open_file(dialog_res)

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()

            self.states.console_display = print_to_console(f"Opened '{filename}'")

        # If dialog was closed pass
        except EmptyFileReturnError as err:
            if hasattr(err, "is_dialog_closed") and err.is_dialog_closed:
                pass
            raise

    # Save the content of the current textbox to the opened file
    # If the content was not saved in a file yet, save to a new IOL file
    def save_file(self, *args):
        try:
            # Check if there are no open tabs then skip
            if self.states.current_tab is None:
                raise EmptyFileReturnError()

            # Get instance of current text box
            curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

            # Save the text in the textbox to the file
            # Returns the name of the IOL file if a new file is created
            # Else if the file exists then save it to current file
            filename = curr_textbox.save_text_to_file()

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()
            self.states.console_display = print_to_console("File saved")

            # If the user saved the content to currently opened file, then skip
            if filename is None:
                return

            self.rename_tab(filename)

        # If the user closed the dialog or if the user tried to save with no tabs open trigger this error
        except EmptyFileReturnError as err:
            if hasattr(err, "is_dialog_closed"):
                return

            if hasattr(err, "message"):
                self.states.console_display = print_to_console(err.message, "error")

    # Save the content of the textbox to IOL or another file type
    def save_file_as(self, *args):
        try:
            # Check if there are no open tabs then skip
            if self.states.current_tab is None:
                raise EmptyFileReturnError()

            # Get instance of current text box
            curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

            # Save the text of the textbox and get the filename
            filename = curr_textbox.save_text_to_file_as()

            self.rename_tab(filename)

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()
            self.states.console_display = print_to_console("File saved")

        # If the user closed the dialog or if the user tried to save with no tabs open trigger this error
        except EmptyFileReturnError as err:
            if hasattr(err, "is_dialog_closed"):
                return

            if hasattr(err, "message"):
                self.states.console_display = print_to_console(err.message, "error")

    # Compile the content in the file
    def compile_file(self, *args):
        try:
            # Check if there are no open tabs then skip
            if self.states.current_tab is None:
                raise EmptyFileReturnError()

            # Get instance of current text box
            curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

            # Gets the modified content of the textbox for compilation
            current_text = curr_textbox.get_compilable_text()

            # Compile the file and get the variables and tokens
            res: dict = compile_file(current_text)

            # Display the variables to the var table
            self.states.var_tables = res['vars']

            # Display to the console that the compilation was successful
            filename = curr_textbox.filename
            response = f"{filename} compiled with no errors found."
            self.states.console_display = print_to_console(response)

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()

        # Throws when the user tries to compile an empty file
        except EmptyFileReturnError as err:
            if hasattr(err, "message"):
                self.states.console_display = print_to_console(err.message, "error")

        # Throws when the format of the IOL file is invalid (No IOL or LOI, or invalid IOL or LOI placements)
        except InvalidIOLFileError as err:
            if hasattr(err, "message"):
                self.states.console_display = print_to_console(err.message, "error")

        # Throws when there is an invalid lexeme then displays all the errors to the console
        except InvalidLexemeError as err:
            if hasattr(err, "error_list"):
                self.states.console_display = print_to_console(err.error_list, "error")


# Container for the textbox
class CodeEditorTextBox(Frame):
    def __init__(self, parent: CodeEditor):
        self._parent_window_size = parent.get_screen_size()

        # Path and filename of the currently opened file
        self.path = ""
        self.filename = ""

        Frame.__init__(self,
                       master=parent,
                       width=self._parent_window_size[0],
                       height=self._parent_window_size[1],
                       background=parent.color_config["bg"])
        self.update_idletasks()

        self.textarea = Text(self,
                             background=parent.color_config["bg"],
                             foreground=parent.color_config["fg"],
                             insertbackground=parent.color_config["fg"],
                             wrap="word")
        self.textarea.pack(side="left", fill="both", expand=True)

        # Set the scroll bar for the code editor
        self.scrollbar = Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.textarea.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.textarea.yview)

        self.grid(column=0, row=0)
        self.grid_propagate(False)

    # Handles the writing of the file content to the textbox
    def handle_text_on_open_file(self, dialog_res):
        try:
            lines, file_path = dialog_res
            # Delete all the text in the textarea
            self.textarea.delete(1.0, 'end')

            self.path = file_path
            self.filename = file_path.split("/")[-1]

            # Insert text from IOL file to the textarea
            for line in lines:
                self.textarea.insert("end", f"{line}\n")

        except IndexError:
            pass

    # Handles the saving of the current content of the textbox to an IOL file
    def save_text_to_file(self):
        try:
            # Get the list of text by line
            current_text = self.textarea.get(1.0, "end").splitlines()

            is_file_new = False

            # An empty file path means that the file was not saved yet
            if self.path == "":
                file_path = filedialog.asksaveasfilename(
                    initialfile="test",
                    initialdir=self.path,
                    title="Save IOL file",
                    filetypes=[("IOL File", ".iol")],
                    defaultextension=".iol"
                )

                # Dialog was closed
                if not file_path:
                    raise EmptyFileReturnError(is_dialog_closed=True)

                self.path = file_path
                self.filename = str(file_path).split("/")[-1]
                is_file_new = True

            write_to_file(self.path, current_text)

            # Return path of file if a new file is created else return None
            return self.filename if is_file_new else None

        except EmptyFileReturnError:
            raise

    # Handles the saving of the current content of the textbox to a file
    def save_text_to_file_as(self):
        try:
            # Get the list of text by line
            current_text = self.textarea.get(1.0, "end").splitlines()

            file_path = filedialog.asksaveasfilename(
                initialfile="test",
                initialdir=self.path,
                title="Save file as...",
                filetypes=[("IOL File", ".iol"), ("Any file", "*.*")],
                defaultextension=".iol"
            )

            # Dialog was closed
            if not file_path:
                raise EmptyFileReturnError(is_dialog_closed=True)

            self.path = file_path
            self.filename = str(file_path).split("/")[-1]

            write_to_file(file_path, current_text)

            # Return new filename
            return self.filename
        except EmptyFileReturnError:
            raise

    # Check and modify the content of the textbox to be compilable
    def get_compilable_text(self):
        try:
            # Get the list of text by line
            current_text = self.textarea.get(1.0, "end").splitlines()

            # Check if the format of the IOL is valid
            if not is_iol_valid(current_text):
                raise InvalidIOLFileError("The syntax of the file is invalid.")

            # Remove the whitespace before and after each line
            current_text = [line.strip() for line in current_text]

            return current_text
        except InvalidIOLFileError:
            raise
