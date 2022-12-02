from tkinter import Frame, Scrollbar, TclError, Menu, filedialog
from tkinter.ttk import Notebook
from utils.StateManager import StateManager
import utils.Utils as utils
from utils.CustomErrors import InvalidIOLFileError, InvalidLexemeError, EmptyFileReturnError
from frames.DisplayTokens import DisplayTokens
from custom_widgets.CustomTextBox import TextLineNumbers, CustomTextWidget
from frames.SyntaxAnalysisWindow import SyntaxAnalysisWindow


# Notebook that contains all tabs for the code editor
class CodeEditorNotebook(Notebook):
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
        ordered_shortcuts = utils.get_shortcuts(get_ordered=True)
        global_shortcuts = ordered_shortcuts["global"]
        local_shortcuts = ordered_shortcuts["local"]

        for action in global_shortcuts:
            tk_key = global_shortcuts[action]["tk_key"]
            if action == "Compile":
                parent.bind(tk_key, self.compile_file)
            elif action == "Show Tokenized Code":
                parent.bind(tk_key, self.show_tokenized_code)
            elif action == "Save":
                parent.bind(tk_key, self.save_file)
            elif action == "Save as":
                parent.bind(tk_key, self.save_file_as)

        self.grid(column=0, row=0, sticky="nsew")
        self.grid_propagate(False)

        # Initializes right-click menu for closing the current tab
        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Close current tab", command=self.close_tab)
        self.bind(local_shortcuts["Tab Options"]["tk_key"], self.open_popup)

        self.color_config = states.color_config

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
            self.states.init_tables()

            return textbox
        except TclError:
            self.states.console_display = utils.print_to_console("Error in adding new tab", "error")

    # Close the current tab
    def close_tab(self):
        # Remove the instance from the textbox list
        self.textbox_list.pop(self.states.current_tab)

        # Remove the states attached to the current tab
        self.states.remove_tab()
        self.forget("current")

    # Updates the index stored in the state manager
    def change_tab(self, event, *_):
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
            dialog_res = utils.open_file("iol")
            filename = dialog_res[1].split("/")[-1]

            # If there are no tabs open create a new tab
            if self.states.current_tab is None:
                curr_textbox: CodeEditorTextBox = self.add_tab(filename)
            else:
                curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

                # If the current textbox is not empty, ask the user if the file should be opened in a new tab
                if len(curr_textbox.textarea.get(1.0, "end")) - 1 > 0 and utils.open_file_prompt():
                    curr_textbox = self.add_tab(filename)
                else:
                    self.rename_tab(filename)

            # Write the content of the file to the textbox
            curr_textbox.handle_text_on_open_file(dialog_res)

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()

            self.states.console_display = utils.print_to_console(f"Opened '{filename}'")

        # If dialog was closed pass
        except EmptyFileReturnError as err:
            has_message = hasattr(err, "is_dialog_closed")
            if has_message and err.is_dialog_closed:
                pass
            elif has_message:
                pass
            raise

    # Save the content of the current textbox to the opened file
    # If the content was not saved in a file yet, save to a new IOL file
    def save_file(self, *_):
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
            self.states.console_display = utils.print_to_console("File saved")

            # If the user saved the content to currently opened file, then skip
            if filename is None:
                return

            self.rename_tab(filename)

        # If the user closed the dialog or if the user tried to save with no tabs open trigger this error
        except EmptyFileReturnError as err:
            if hasattr(err, "is_dialog_closed"):
                return

            if hasattr(err, "message"):
                self.states.console_display = utils.print_to_console(err.message, "error")

    # Save the content of the textbox to IOL or another file type
    def save_file_as(self, *_):
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
            self.states.console_display = utils.print_to_console("File saved")

        # If the user closed the dialog or if the user tried to save with no tabs open trigger this error
        except EmptyFileReturnError as err:
            if hasattr(err, "is_dialog_closed"):
                return

            if hasattr(err, "message"):
                self.states.console_display = utils.print_to_console(err.message, "error")

    # Compile the content in the file
    def compile_file(self, *_):
        try:
            # Check if there are no open tabs then skip
            if self.states.current_tab is None:
                raise EmptyFileReturnError()

            # Get instance of current text box
            curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

            # Gets the modified content of the textbox for compilation
            current_text = curr_textbox.get_compilable_text()

            # Compile the file and get the variables and tokens
            res: dict = utils.compile_file(current_text)

            # Display the variables to the var table
            self.states.var_tables = res['vars']

            # Display to the console that the compilation was successful
            filename = curr_textbox.filename

            # Save tokens to token file
            utils.write_to_tkn_file(filename, res['tokens'])

            # Perform Syntax Analysis
            SyntaxAnalysisWindow(self)

            response = f"{filename} compiled with no errors found."
            self.states.console_display = utils.print_to_console(response)

            # Triggers an OS-dependent chime to notify the user the file successfully saved
            self.bell()

            self.show_tokenized_code(token_list=res['tokens'])
            curr_textbox.is_compiled = True

        # Throws when the user tries to compile an empty file
        except EmptyFileReturnError as err:
            if hasattr(err, "message"):
                self.states.console_display = utils.print_to_console(err.message, "error")

        # Throws when the format of the IOL file is invalid (No IOL or LOI, or invalid IOL or LOI placements)
        except InvalidIOLFileError as err:
            if hasattr(err, "message"):
                self.states.console_display = utils.print_to_console(err.message, "error")

        # Throws when there is an invalid lexeme then displays all the errors to the console
        except InvalidLexemeError as err:
            if hasattr(err, "error_list"):
                self.states.console_display = utils.print_to_console(err.error_list, "error")

        # Throws when chosen file does not exist
        except FileNotFoundError:
            self.states.console_display = utils.print_to_console("File does not exist", "error")

    def show_tokenized_code(self, *events, token_list=None, **__):
        if self.states.current_tab is None:
            return

        if token_list is None:
            # Get instance of current text box
            curr_textbox: CodeEditorTextBox = self.textbox_list[self.states.current_tab]

            if not curr_textbox.is_compiled:
                self.states.console_display = utils.print_to_console("No file was compiled", "error")
                return

            filename = curr_textbox.filename
            token_list = utils.get_tokens_from_file(filename)

        DisplayTokens(self, token_list)

    def get_values_from_window(self, values):
        self.states.console_display = utils.print_to_console(values)


# Container for the textbox
class CodeEditorTextBox(Frame):
    def __init__(self, parent: CodeEditorNotebook):
        self._parent_window_size = parent.get_screen_size()

        # Path and filename of the currently opened file
        self.path = ""
        self.filename = ""
        self.is_compiled = False

        Frame.__init__(self,
                       master=parent,
                       width=self._parent_window_size[0],
                       height=self._parent_window_size[1],
                       background=parent.color_config["bg"])
        self.update_idletasks()

        self.textarea = CustomTextWidget(self,
                                         background=parent.color_config["bg"],
                                         foreground=parent.color_config["fg"],
                                         insertbackground=parent.color_config["fg"],
                                         wrap="word")

        # Set the scroll bar for the code editor
        self.scrollbar = Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.scrollbar.config(command=self.textarea.yview)

        self.line_numbers = TextLineNumbers(self, width=30, background=parent.color_config["bg"])
        self.line_numbers.attach(self.textarea)

        self.textarea.bind("<<Change>>", self._on_change)
        self.textarea.bind("<<Configure>>", self._on_change)

        self.textarea.config(yscrollcommand=self.scrollbar.set)
        self.line_numbers.pack(side="left", fill="y")
        self.textarea.pack(side="right", fill="both", expand=True)

        self.grid(column=0, row=0)
        self.grid_propagate(False)

    def _on_change(self, *_):
        self.line_numbers.redraw()

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

            utils.write_to_file(self.path, current_text)

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

            utils.write_to_file(file_path, current_text)

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
            if not utils.is_iol_valid(current_text):
                raise InvalidIOLFileError("The syntax of the file is invalid.")

            # Remove the whitespace before and after each line
            current_text = [line.strip() for line in current_text]

            return current_text
        except InvalidIOLFileError:
            raise
