# Copyright 2021, Andres Fredes, <andres.hector.fredes@gmail.com>
# 
# This file is part of timesheet.
# 
#     timesheet is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     timesheet is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with timesheet.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QFont, QRegularExpressionValidator
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import (QAction, QComboBox, QLabel, QLineEdit,
                             QPushButton)

class Action(QAction):
    def __init__(self, name, window, shortcut, tip, func):
        super().__init__(name, window)
        self.setShortcut(shortcut)
        self.setStatusTip(tip)
        self.triggered.connect(func)


class Label(QLabel):
    def __init__(self, text="", size=20, style=None):
        super().__init__()
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        font = Font(size, style)
        self.setFont(font)


class Font(QFont):
    def __init__(self, size=20, style=None):
        super().__init__()
        self.setPointSize(size)
        if style == "strike":
            self.setStrikeOut(True)
        if style == "italic:":
            self.setItalic(True)
        if style == "bold":
            self.setBold(True)


class Text_Box(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFont(Font())


class Combo_Box(QComboBox):
    def __init__(self, items=[], func=None):
        super().__init__()
        self.addItems(items)
        if func:
            self.activated.connect(func)
        self.setFont(Font())


class Button(QPushButton):
    def __init__(self, text="", func=None):
        super().__init__()
        self.setText(text)
        if func:
            self.clicked.connect(func)
        self.setFont(Font())

class RegEx_Validator(QRegularExpressionValidator):
    def __init__(self, pattern):
        re = QRegularExpression(pattern)
        super().__init__(re)

class Database(QSqlDatabase):
    def __init__(self, filename):
        super().__init__('QSQLITE')
        self.setDatabaseName(filename)