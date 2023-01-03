# Errors pertaining to the IOL file
class InvalidIOLFileError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message


# Errors caught during compilation of the lexemes
class InvalidLexemeError(Exception):
    def __init__(self, errors: list):
        Exception.__init__(self)
        self.error_list = []
        for error in errors:
            self.error_list.append(f"Invalid token '{error[0]}' in line {error[1]}")


class InvalidSyntaxError(Exception):
    def __init__(self, errors: list):
        Exception.__init__(self)
        self.error_list = [error for error in errors]


# Errors due to invalid actions when the code editor is empty
class EmptyFileReturnError(Exception):
    def __init__(self, is_dialog_closed=None):
        Exception.__init__(self)
        if is_dialog_closed:
            self.is_dialog_closed = True
        self.message = "Cannot perform action since current file is empty"


# Errors due to invalid prod file
class InvalidProdFileError(Exception):
    def __init__(self, filename: str, line: int):
        Exception.__init__(self)
        self.message = f"Production file: {filename}.prod has an error in line {line}"


# Errors due to invalid prod file
class InvalidParseTableError(Exception):
    def __init__(self, filename: str, line: int):
        Exception.__init__(self)
        self.message = f"Rule file: {filename}.prod has an error in line {line}"


# General errors on execution
class ExecutionError(Exception):
    def __init__(self, filename: str, message="Unknown error during execution."):
        Exception.__init__(self)
        self.message = f"Failed to execute {filename}, due to '{message}'"


# General errors on execution
class TypeMismatchError(Exception):
    def __init__(self):
        Exception.__init__(self)
        self.message = "Inputted value does not match the expected type."
