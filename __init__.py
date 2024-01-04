from pathlib import Path
from binaryninja import *


# Note that this is a sample plugin and you may need to manually edit it with
# additional functionality. In particular, this example only passes in the
# binary view. If you would like to act on an addres or function you should
# consider using other register_for* functions.

# Add documentation about UI plugin alternatives and potentially getting
# current_* functions

def main(bv):
    # Copyright (c) 2015-2023 Vector 35 Inc
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to
    # deal in the Software without restriction, including without limitation the
    # rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    # sell copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    # IN THE SOFTWARE.

    # This is an example UI plugin which demonstrates how to add sidebar widgets to Binary Ninja.
    # See .../api/ui/sidebar.h for interface details.

    from binaryninjaui import SidebarWidget, SidebarWidgetType, Sidebar, UIActionHandler
    from PySide6.QtWidgets import QVBoxLayout, QListWidget, QLineEdit
    from PySide6.QtGui import QImage
    import PySide6.QtCore as QtCore

    symbols_comments_list = []

    # Sidebar widgets must derive from SidebarWidget, not QWidget. SidebarWidget is a QWidget but
    # provides callbacks for sidebar events, and must be created with a title.
    class CommentsAndSymbolsWidget(SidebarWidget):
        def __init__(self, name, frame, data):
            SidebarWidget.__init__(self, name)
            self.actionHandler = UIActionHandler()
            self.actionHandler.setupActionHandler(self)

            self.layout = QVBoxLayout()
            self.widget = QListWidget()

            self.line_edit = QLineEdit()
            self.line_edit.setMaxLength(10)
            self.line_edit.setPlaceholderText("Filter your search")
            self.line_edit.textChanged.connect(self.filter_text)
            self.line_edit.returnPressed.connect(self.return_pressed)

            self.add_symbols()
            self.add_comments()

            self.widget.currentTextChanged.connect(self.text_changed)
            self.layout.addWidget(self.line_edit)
            self.layout.addWidget(self.widget)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)

            self.setLayout(self.layout)

        def add_comments(self):
            for x in range(bv.start, bv.end):
                comment = bv.get_comment_at(x)
                if comment:
                    f_comment = f"[+] {hex(x)} - {comment}"
                    symbols_comments_list.append(f_comment)
                    self.widget.addItem(f_comment)

        def add_symbols(self):
            for symbol in bv.symbols.items():
                label = symbol[0]

                if label.startswith('__'):
                    continue

                addr = int(str(bv.symbols.get(label)).split('>')[0].split('@')[1].replace('x', '').strip(), 16)

                f_symbol = f"[+] {hex(addr)} - {label}"
                symbols_comments_list.append(f_symbol)
                self.widget.addItem(f_symbol)

        def text_changed(self, s):
            print(s)

        def filter_text(self, s):
            self.widget.clear()
            rex_ex = QtCore.QRegularExpression(s)
            filter_files = [x for x in symbols_comments_list if rex_ex.match(x).hasMatch()]
            self.widget.addItems(filter_files)

        def return_pressed(self):
            self.widget.clear()
            self.widget.addItems(symbols_comments_list)

    root = Path(__file__).parent

    class CommentsAndSymbolsWidgetType(SidebarWidgetType):
        def __init__(self):
            # Sidebar icons are 28x28 points. Should be at least 56x56 pixels for
            # HiDPI display compatibility. They will be automatically made theme
            # aware, so you need only provide a grayscale image, where white is
            # the color of the shape.
            icon = QImage(str(root.joinpath("comments.png")))

            SidebarWidgetType.__init__(self, icon, "Comments and Symbols")

        def createWidget(self, frame, data):
            # This callback is called when a widget needs to be created for a given context. Different
            # widgets are created for each unique BinaryView. They are created on demand when the sidebar
            # widget is visible and the BinaryView becomes active.
            return CommentsAndSymbolsWidget("Comments and Symbols", frame, data)

    # Register the sidebar widget type with Binary Ninja. This will make it appear as an icon in the
    # sidebar and the `createWidget` method will be called when a widget is required.
    Sidebar.addSidebarWidgetType(CommentsAndSymbolsWidgetType())


PluginCommand.register('CommentsAndSymbols', 'CommentsAndSymbols', main)
