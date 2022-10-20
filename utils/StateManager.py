from frames.VarTable import VarTable
from frames.Console import Console


# Custom class that follows the observer pattern to notify subscribed classes for any changes connected
# to the specified variables
class Subject:
    def __init__(self):
        self._observers: list[VarTable | Console] = []

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

        # Collects the list variables to be displayed in each variable table of all tabs
        self.__var_tables: list = []

        # Intermediate variable that contains the values to be displayed in the console
        self.__console_display: str | list[str] | None = None

    @property
    def current_tab(self):
        return self.__current_tab

    @property
    def var_tables(self):
        return self.__var_tables

    @property
    def console_display(self):
        return self.__console_display

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

    # Updates the current text to be displayed in the console window
    @console_display.setter
    def console_display(self, data):
        self.__console_display = data

        # Notifies observers for changes
        self.notify()

    # Assign an empty list of variables for the new tab
    def init_var_table(self):
        self.__var_tables.append([])

    # Update variables when a tab was removed
    def remove_tab(self):
        idx = self.__current_tab
        self.__console_display = None
        self.__var_tables.pop(idx)
        self.__current_tab = None
