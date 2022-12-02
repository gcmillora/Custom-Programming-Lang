from tkinter import filedialog, messagebox
from utils.CustomErrors import EmptyFileReturnError, InvalidLexemeError, InvalidSyntaxError
from typing import Literal
from compiler.processes import syntax_analysis

__FileTypes = Literal["iol", "prod", "ptbl"]


# Open local files
def open_file(file_type: __FileTypes | list[__FileTypes] | None,
              title: str = "Select File"):
    try:
        filetypes_to_ask = []
        if file_type is None:
            filetypes_to_ask.append(("All file types", "*.*"))
        else:
            if type(file_type) != list:
                file_type = [file_type]

            for curr_file_type in file_type:
                if curr_file_type == "iol":
                    filetypes_to_ask.append(("Integer-Oriented Language File", "*.iol"))
                if curr_file_type == "prod":
                    filetypes_to_ask.append(("Production File", "*.prod"))
                if curr_file_type == "ptbl":
                    filetypes_to_ask.append(("Parse Table File", "*.ptbl"))

        # Open folder via filedialog
        filename: filedialog = filedialog.askopenfilename(title=title,
                                                          filetypes=(*filetypes_to_ask,))

        # Dialog was closed
        if not filename:
            raise EmptyFileReturnError(is_dialog_closed=True)

        # Open file and get the content inside
        with open(f"{filename}", "r") as file:
            try:
                return file.read().splitlines(), filename
            except IndexError:
                raise

    except EmptyFileReturnError:
        raise


# Open MessageBox
def open_file_prompt():
    return messagebox.askyesno("Open existing file", "Do you want to open file in new tab?")


# Compile the file and return the tokens and variables
def compile_file(lines: list[str]):
    tokens = []
    variables = []
    errors = []
    keywords = ["ADD", "SUB", "MULT", "DIV", "MOD", "INTO",
                "IS", "BEG", "PRINT", "INT", "STR", "DEFINE", "NEWLN"]

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
                tokens.append((word, "IDENT", idx))
                variables.append((word, "IDENT", idx))
            else:
                tokens.append((word, "ERR_LEX", idx))
                errors.append((word, idx))

    # If errors were found then return the error list only
    if len(errors) > 1:
        raise InvalidLexemeError(errors)

    success, error_line = syntax_analysis(tokens)
    print(error_line)
    if not success:
        raise InvalidSyntaxError(error_line)

    return {
        "tokens": tokens,
        "vars": variables,
    }


# Write text from code editor to iol file
def write_to_file(file_path, current_text):
    with open(file_path, "a+") as file:
        file.truncate(0)
        file.writelines(f"{line} \n" for line in current_text)


# Write tokens to tkn file
def write_to_tkn_file(filename, tokens):
    # Create file_path for tokens
    filename = filename.split('.')[0]
    file_path = f"./_out/{filename}.tkn"

    # Convert list/array of tuple to list/array of strings
    new_token_list: list[str] = [",".join(map(str, token_row)) for token_row in tokens]

    write_to_file(file_path, new_token_list)


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
def print_to_console(text: str | list[str], log_type: Literal["info", "error", "success"] = "info"):
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


# Get tokenized code
def get_tokens_from_file(filename: str):
    try:
        # Open file_path for tokens
        filename = filename.split('.')[0]
        file_path = f"./_out/{filename}.tkn"

        with open(file_path, "r") as token_file:
            return [tuple(lines.strip().split(",")) for lines in token_file]
    except FileNotFoundError:
        return None


# Get all set shortcuts
def get_shortcuts(get_all=True, get_ordered=False):
    global_shortcuts = {
        "Compile": {
            "tk_key": "<Control-p>",
            "desc": "Compile the code on the code editor.",
            "key": "Ctrl + P",
        },
        "Show Tokenized Code": {
            "tk_key": "<Control-t>",
            "desc": "Show the tokenized code in a window.",
            "key": "Ctrl + T",
        },
        "Save": {
            "tk_key": "<Control-s>",
            "desc": "Save the file to the current or new file.",
            "key": "Ctrl + S",
        },
        "Save as": {
            "tk_key": "<Control-Shift-s>",
            "desc": "Save the file to a new file format.",
            "key": "Ctrl + Shift + S",
        },
    }

    local_shortcuts = {
        "Tab Options": {
            "tk_key": "<Button-3>",
            "desc": "Right click the tab name to open the menu to close the tab.",
            "key": "Right Click (MB3)",
        },
    }

    if get_ordered:
        return {"global": global_shortcuts, "local": local_shortcuts}

    if get_all:
        return {**global_shortcuts, **local_shortcuts}
