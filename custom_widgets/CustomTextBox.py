from tkinter import Text, Canvas


# Reference: https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget

class TextLineNumbers(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.current_text_box = None

    def attach(self, text_widget):
        self.current_text_box = text_widget

    def redraw(self, *args):
        """redraw line numbers"""
        self.delete("all")

        i = self.current_text_box.index("@0,0")
        dline = self.current_text_box.dlineinfo(i)

        while dline is not None:
            line_num = str(i).split(".")[0]
            self.create_text(2, dline[1], anchor="nw",
                             text=line_num,
                             fill="white")
            i = self.current_text_box.index("%s+1line" % i)
            dline = self.current_text_box.dlineinfo(i)


class CustomTextWidget(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or
                args[0:3] == ("mark", "set", "insert") or
                args[0:2] == ("xview", "moveto") or
                args[0:2] == ("xview", "scroll") or
                args[0:2] == ("yview", "moveto") or
                args[0:2] == ("yview", "scroll")):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result
