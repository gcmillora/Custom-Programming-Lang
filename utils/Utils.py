from tkinter import filedialog, messagebox
from utils.CustomErrors import EmptyFileReturnError, InvalidLexemeError


# Open local iol file
def open_filedialog():
    try:
        # Open folder via filedialog
        filename: filedialog = filedialog.askopenfilename(title='Select File',
                                                          filetypes=(
                                                              ("Integer-Oriented Language File", "*.iol"),))

        # Dialog was closed
        if not filename:
            raise EmptyFileReturnError(is_dialog_closed=True)

        # Open file and get the content inside
        with open(f"{filename}", "r") as iol:
            try:
                return iol.read().splitlines(), filename
            except IndexError:
                raise

    except EmptyFileReturnError:
        raise


# Open MessageBox
def open_file_prompt():
    return messagebox.askyesno("Open existing file", "Do you want to open file in new tab?")


# Compile the file and return the tokens and variables
def compile_file(lines: list[str]):
    try:
        tokens = []
        variables = []
        errors = []
        keywords = ["ADD", "SUB", "MULT", "DIV", "MOD", "INTO", "IS", "BEG", "PRINT", "INT", "STR", "DEFINE", "NEWLN"]

        # TODO: Add comments
        for idx, line in enumerate(lines, start=1):
            lexemes = line.split(" ")
            if line == "":
                continue
            if line == "IOL" or line == "LOI":
                continue
            for word in lexemes:
                if word in keywords:
                    tokens.append((word, word, idx))
                elif word.isnumeric():
                    tokens.append((word, "INT_LIT", idx))
                elif word[0].isalpha() and word.isalnum():
                    variables.append((word, "IDENT", idx))
                else:
                    tokens.append((word, "ERR_LEX", idx))
                    errors.append((word, idx))

        # If errors were found then return the error list only
        if len(errors) > 1:
            raise InvalidLexemeError(errors)

        return {
            "tokens": tokens,
            "vars": variables,
        }

    except InvalidLexemeError:
        raise


# Write text from code editor to iol file
def write_to_file(file_path, current_text):
    with open(file_path, "a+") as file:
        file.truncate(0)
        file.writelines(f"{line} \n" for line in current_text)


# Check if the contents of the iol file is valid
def is_iol_valid(lines: list[str]) -> bool:
    iol_found = False
    content_found = False
    loi_found = False
    for line in lines:
        # Remove the whitespaces before and after the line
        line = line.strip()
        # The valid sequence of content is 'IOL', content, then 'LOI'
        if line == "IOL":
            # If another 'IOL' is found it is invalid
            if iol_found:
                return False
            iol_found = True
        elif line == "LOI":
            # If the line is 'LOI' and the 'IOL' has not been found it is invalid
            # or if another 'LOI' is found it is invalid
            if not iol_found or loi_found:
                return False
            loi_found = True
        elif line == "":
            # If the line is an empty space then skip
            continue
        else:
            # If the 'IOL' has not been found before the content is it invalid
            # or if the content has been found and the 'LOI' has been found, it is also invalid
            if not iol_found or loi_found:
                return False
            elif content_found:
                continue
            content_found = True

    return iol_found and loi_found


# Formats the text to be displayed to the console
def print_to_console(text: str | list[str], log_type: str = "info"):
    log_type = log_type.upper()
    if type(text) is list:
        final_disp = []
        # Add log type to the start of every string to the status
        for line in text:
            final_disp.append(f"{log_type}: {line}")
        return final_disp
    else:
        # Add log type to the start of the string to the status
        return f"{log_type}: {text}"
