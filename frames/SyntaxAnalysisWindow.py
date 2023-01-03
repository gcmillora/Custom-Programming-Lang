from tkinter import Toplevel, Scrollbar, Frame, Label, Button, StringVar, Text
from tkinter.ttk import Treeview
from utils.Utils import open_file, write_to_file
from compiler.processes import check_and_clean_prod, check_and_clean_parse
from utils.CustomErrors import InvalidProdFileError, InvalidParseTableError
from compiler.processes import parsing
from copy import deepcopy


class SyntaxAnalysisWindow(Toplevel):
    def __init__(self, root):
        Toplevel.__init__(self, root)
        self.geometry("500x502")
        self.title("Syntax Analysis")

        self.prod_table = Table(self, "Production", columns=("ID", "NT", "P"))
        self.prod_table.grid(column=0, row=0)

        self.parse_table = Table(self, "Parse Table", columns=("", "id"))
        self.parse_table.grid(column=1, row=0)

        self.__status_text = StringVar(self, value="Upload a new file.")

        UploadField(self, self.__status_text).grid(columnspan=2, row=1, sticky="we")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def upload_file(self):
        filename = "Upload failed."
        try:
            file, filename = open_file(["prod", "ptbl"])
            file_type = filename.split(".")[-1]
            filename = str(filename).split("/")[-1]

            if file_type == "prod":
                cleaned_file = check_and_clean_prod(file, filename)
                self.prod_table.add_values(cleaned_file, filename)
            else:
                cleaned_file = check_and_clean_parse(file, filename)
                self.parse_table.add_values(cleaned_file, filename, True)

            self.__status_text.set(f"LOADED: {filename}")

            if self.prod_table.values is not None and self.parse_table.values is not None:
                self.generate_input_frame()

        except InvalidProdFileError as err:
            self.__status_text.set(f"FAILED: {filename}")
            if hasattr(err, "message"):
                return err
            raise

        except InvalidParseTableError as err:
            self.__status_text.set(f"FAILED: {filename}")
            if hasattr(err, "message"):
                return err
            raise

    def generate_input_frame(self):
        ParsingField(self, self.prod_table.values, self.parse_table.values).grid(columnspan=2, row=2)


class Table(Frame):
    def __init__(self, parent: SyntaxAnalysisWindow, title: str, columns: tuple):
        Frame.__init__(self,
                       master=parent)

        # Stored values
        self.values: list | None = None

        self.parent = parent

        self.__table = Treeview(self,
                                columns=columns,
                                height=10)
        self.__table.tag_configure("oddrow", background="#ced4da")

        self.__table.column("#0", width=0, stretch=False)
        self.__table.heading("#0", text="", anchor="center")

        self.__table_width = int(parent.winfo_reqwidth() * 0.35)

        for column_name in columns:
            self.__table.column(column_name, anchor="center", width=self.__table_width)
            self.__table.heading(column_name, text=column_name, anchor="center")

        self.__scrollbar = Scrollbar(self, orient="vertical")
        self.__table.config(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.config(command=self.__table.yview)

        Label(self, text=title).pack(side="top", expand=False)
        self.__file_name = Label(self, text="No file uploaded.")
        self.__file_name.pack(side="top", expand=False)
        self.__scrollbar.pack(side="right", fill="y")
        self.__table.pack(side="left", fill="both", expand=True)

    def clear_table(self):
        self.__table.delete(*self.__table.get_children())

    def add_values(self, data: list, filename: str, is_parse_table=False):
        # Clear the table before inserting new values
        self.clear_table()
        data_copy = deepcopy(data)

        if is_parse_table:
            self.add_columns(data_copy[0])
            data_copy = data_copy[1:]

        for idx, line in enumerate(data_copy):
            # Set table insert options
            options = {
                "parent": "",
                "index": "end",
            }

            if idx % 2 != 0:
                options["tags"] = "oddrow"
            self.__table.insert(**options, values=line)

        self.values = data if is_parse_table else data_copy
        self.__file_name.configure(text=filename)

    def add_columns(self, headings: list):
        self.__table.pack_forget()
        # Update with new columns
        self.__table['columns'] = tuple(headings)
        for key in headings:
            self.__table.column(key, anchor="center", width=self.__table_width)
            self.__table.heading(key, text=key, anchor="center")
        self.__table.pack(side="left", fill="both", expand=True)
        new_width = len(headings) * int(self.__table_width * 1.5)
        self.parent.geometry(f"{new_width}x502")


class UploadField(Frame):
    def __init__(self, parent, text_variable):
        Frame.__init__(self,
                       parent,
                       width=parent.winfo_reqwidth())

        self.__upload_button = Button(self, text="Upload file", command=parent.upload_file)
        self.__upload_button.grid(column=0, row=0, sticky="w")

        Label(self, textvariable=text_variable).grid(column=1, row=0, sticky="e")


class ParsingField(Frame):
    def __init__(self, parent, prod_table, parse_table):
        Frame.__init__(self,
                       parent,
                       width=parent.winfo_reqwidth(),
                       height=parent.winfo_reqheight())

        self.prod_table = prod_table
        self.parse_table = parse_table
        self.result_table: str | None = None

        input_field = Frame(self, width=self.winfo_reqwidth())
        input_field.pack(side="top", fill="x", expand=True)

        Label(input_field, text="INPUT").grid(column=0, row=0, sticky="w")
        self.text_box = Text(input_field, height=1, width=50)
        self.text_box.grid(column=1, row=0, sticky='we')

        Button(input_field, text="Parse", command=self.parse_values).grid(column=2, row=0, sticky="e")

        result_area = Frame(self, width=self.winfo_reqwidth(), height=self.winfo_reqheight())
        result_area.pack(side="bottom", fill="x", expand=True)

        self.status = StringVar(self, value="PARSING:")
        Label(result_area, textvariable=self.status).pack(side="top", expand=True, fill="x")

        self.__result_table = Treeview(result_area,
                                       columns=("stack", "buffer", "action"),
                                       height=15)
        self.__result_table.tag_configure("oddrow", background="#ced4da")
        self.__table_width = int(parent.winfo_reqwidth() * 0.35)

        self.__result_table.column("#0", width=0, stretch=False)
        self.__result_table.column("stack", width=0, anchor="center")
        self.__result_table.column("buffer", width=0, anchor="center")
        self.__result_table.column("action", width=0, anchor="center")

        self.__result_table.heading("#0", text="", anchor="center")
        self.__result_table.heading("stack", text="STACK", anchor="center")
        self.__result_table.heading("buffer", text="INPUT BUFFER", anchor="center")
        self.__result_table.heading("action", text="ACTION", anchor="center")

        self.__scrollbar = Scrollbar(result_area, orient="vertical")
        self.__result_table.config(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.config(command=self.__result_table.yview)
        self.__scrollbar.pack(side="right", fill="y")
        self.__result_table.pack(side="left", fill="both", expand=True)

    def clear_table(self):
        self.__result_table.delete(*self.__result_table.get_children())

    def parse_values(self):
        try:
            result = parsing(self.prod_table,
                             self.parse_table,
                             self.text_box.get(1.0, 'end').strip().split(' '))
            result = result.splitlines()

            self.clear_table()
            for idx, line in enumerate(result):
                line = line.split(",")
                # Set table insert options
                options = {
                    "parent": "",
                    "index": "end",
                }

                if idx % 2 != 0:
                    options["tags"] = "oddrow"
                self.__result_table.insert(**options, values=line)

            write_to_file("./_out/test_rules.prsd", result)
        except InvalidParseTableError:
            self.status.set("PARSING: Invalid. Please see test_results.prsd")
