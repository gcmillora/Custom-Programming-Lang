from frames.VarTableContainer import VarTableContainer
from frames.Console import Console
from custom_widgets.BegWindow import BegWindow


# Custom class that follows the observer pattern to notify subscribed classes for any changes connected
# to the specified variables
class Subject:
    def __init__(self):
        self._observers: list[VarTableContainer | Console] = []

    def notify(self, modifier=None):
        # Calls the notify method of subscribed observers
        for observer in self._observers:
            if modifier != observer:
                observer.notify(self)

    def subscribe(self, observer):
        # Adds the observer to the list
        if observer not in self._observers:
            self._observers.append(observer)


# Class that contains variables that can trigger methods or events in other classes when their values changes
class StateManager(Subject):
    def __init__(self):
        Subject.__init__(self)

        # Tracks the current tab in focus
        self.__current_tab: int | None = None

        # Collects the list of variables to be displayed in each variable tables of all tabs
        self.__var_tables: list = []

        # Collects the list of production values to be displayed in each prod tables of all tabs
        self.__prod_tables: list = []

        # Collects the list of parse table values to be displayed in each parse tables of all tabs
        self.__parse_tables: list = []

        # Intermediate variable that contains the values to be displayed in the console
        self.__console_display: str | list[str] | None = None

        # Event to clear the console
        self.__to_clear_console: bool = False

        # Temporary cache for the input value
        self.__user_input: str | None = None

        # Color configuration of the program
        self.color_config = {
            "bg": "#37474F",
            "fg": "#ECEFF1",
            "alt_bg": "#22223b"
        }

    @property
    def current_tab(self):
        return self.__current_tab

    @property
    def var_tables(self):
        return self.__var_tables

    @property
    def prod_tables(self):
        return self.__prod_tables

    @property
    def parse_tables(self):
        return self.__parse_tables

    @property
    def console_display(self):
        return self.__console_display

    # Revert to console to cleared on GET
    @property
    def to_clear_console(self):
        if self.__to_clear_console:
            self.__to_clear_console = False
            return True
        return False

    # Clears the current cached value after fetching it
    @property
    def user_input(self):
        temp = self.__user_input
        self.__user_input = None
        return temp

    # Sets the index of the current tab
    @current_tab.setter
    def current_tab(self, tab_name: str):
        self.__current_tab = tab_name

        # Notifies observers for changes
        self.notify()

    # Sets the variables for the var table in the current tab
    @var_tables.setter
    def var_tables(self, data):
        idx = self.__current_tab

        # If the variables are redundant, then skip
        if data in self.__var_tables:
            return

        # If there are no code editor tabs, then skip
        if idx is None:
            return

        # Set the variables to the var table in the current tab
        self.__var_tables[idx] = data

        # Notifies observers for changes
        self.notify()

    # Sets the variables for the var table in the current tab
    @prod_tables.setter
    def prod_tables(self, data):
        idx = self.__current_tab

        # If the values are redundant, then skip
        if data in self.__prod_tables:
            return

        # If there are no code editor tabs, then skip
        if idx is None:
            return

        # Set the values to the prod table in the current tab
        self.__prod_tables[idx] = data

        # Notifies observers for changes
        self.notify()

    # Sets the variables for the var table in the current tab
    @parse_tables.setter
    def parse_tables(self, data):
        idx = self.__current_tab

        # If the values are redundant, then skip
        if data in self.__parse_tables:
            return

        # If there are no code editor tabs, then skip
        if idx is None:
            return

        # Set the values to the parse table in the current tab
        self.__parse_tables[idx] = data

        # Notifies observers for changes
        self.notify()

    # Updates the current text to be displayed in the console window
    @console_display.setter
    def console_display(self, data):
        self.__console_display = data

        # Notifies observers for changes
        self.notify()

    # Call to trigger to clear the console screen
    def clear_console(self):
        if not self.__to_clear_console:
            self.__to_clear_console = True

            # Notifies observers for changes
            self.notify()

    # Update the current user input cache
    def __update_user_input(self, user_input):
        self.__user_input = user_input

    # Assign an empty list of tables for the new tab
    def init_tables(self):
        self.__var_tables.append([])
        self.__prod_tables.append([])
        self.__parse_tables.append([])

    # Update variables when a tab was removed
    def remove_tab(self):
        idx = self.__current_tab
        self.__console_display = None
        self.__var_tables.pop(idx)
        self.__prod_tables.pop(idx)
        self.__parse_tables.pop(idx)
        self.__current_tab = None

    # Opens a window to get user input
    def beg_user(self, parent, label="Input Value"):
        popup = BegWindow(parent, self.__update_user_input, label)
        parent.wait_window(popup)
        return self.user_input
