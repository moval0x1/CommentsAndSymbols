import binaryninjaui
import PySide6.QtCore as QtCore

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton

from pathlib import Path

symbols_comments_list = []


class CommentsAndSymbolsDialog(QDialog):
    def __init__(self, bv):
        super(CommentsAndSymbolsDialog, self).__init__()
        global symbols_comments_list
        self.bv = bv

        self.setWindowTitle("Show Comments and Renamed Symbols")
        self.setGeometry(1200, 200, 500, 800)

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()

        self.line_edit = QLineEdit()
        self.line_edit.setMaxLength(10)
        self.line_edit.setPlaceholderText("Filter your search")
        self.line_edit.textChanged.connect(self.filter_text)
        self.line_edit.returnPressed.connect(self.return_pressed)
        self.line_edit.setMaxLength(30)

        self.button = QPushButton('Refresh')
        self.button.clicked.connect(self.button_clicked)

        self.add_symbols()
        self.add_comments()

        self.list_widget.currentTextChanged.connect(self.text_changed)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.list_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def button_clicked(self):
        self.line_edit.clear()
        symbols_comments_list.clear()
        self.add_symbols()
        self.add_comments()


    def add_item_lst(self, item):
        if item in symbols_comments_list:
            return

        symbols_comments_list.append(item)

    def add_comments(self):
        for x in range(self.bv.start, self.bv.end):
            comment = self.bv.get_comment_at(x)
            if comment:
                f_comment = f"[+] {hex(x)} - {comment}"
                self.add_item_lst(f_comment)
                self.list_widget.addItem(f_comment)

    def add_symbols(self):
        for symbol in self.bv.symbols.items():
            label = symbol[0]

            if label.startswith('__'):
                continue

            addr = int(str(self.bv.symbols.get(label)).split('>')[0].split('@')[1].replace('x', '').strip(), 16)

            f_symbol = f"[+] {hex(addr)} - {label}"
            self.add_item_lst(f_symbol)
            self.list_widget.addItem(f_symbol)

    def text_changed(self, s):
        print(s)

    def filter_text(self, s):
        self.list_widget.clear()
        rex_ex = QtCore.QRegularExpression(s)
        filter_files = [x for x in symbols_comments_list if rex_ex.match(x).hasMatch()]
        self.list_widget.addItems(filter_files)

    def return_pressed(self):
        self.list_widget.clear()
        self.list_widget.addItems(symbols_comments_list)


def comments_and_symbols(bv):
    assert QApplication.instance() is not None

    global dialog
    dialog = CommentsAndSymbolsDialog(bv)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()