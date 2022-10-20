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


# Errors due to invalid actions when the code editor is empty
class EmptyFileReturnError(Exception):
    def __init__(self, is_dialog_closed=None):
        Exception.__init__(self)
        if is_dialog_closed:
            self.is_dialog_closed = True
        self.message = "Cannot perform action since current file is empty"
