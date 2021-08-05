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

"""Timesheet: task/project time keeping program.

custom_widgets.py holds the subclassed widgets with program-specific
functionality. A UI is made of many widgets, many of which share styling or
functional elements with their fellows.
Most/all of these widgets have been designed to allow for a single line
instantiation within the core code without further adjustment.
"""

from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QFont, QRegularExpressionValidator
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import (QAction, QComboBox, QLabel, QLineEdit,
                             QPushButton)

class Action(QAction):
    """A menu option with associated function, keyboard shortcut and status tip.

    Args:
        name (str): menu option name.
        window (QMainWindow): the menu's parent window.
        shortcut (str): keyboard shortcut for the menu option.
        func (function): function to be called when menu option is selected.
    """
    def __init__(self, name, window, shortcut, tip, func):
        super().__init__(name, window)
        self.setShortcut(shortcut)
        self.setStatusTip(tip)
        self.triggered.connect(func)


class Label(QLabel):
    """A label widget with defined inner text, size and font style.

    Args:
        text (str): text to be displayed.
        size (int): font point size. Defaults to 20.
        style (str): font style ('strike', 'bold' or 'italic').
            Defaults to None.
    """
    def __init__(self, text="", size=20, style=None):
        super().__init__()
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        font = Font(size, style)
        self.setFont(font)


class Font(QFont):
    """A font element to be included in labels and other widgets that display
    text.

    Args:
        size (int): font point size. Defaults to 20.
        style (str): font style ('strike', 'bold' or 'italic').
            Defaults to None.
    """
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
    """A text box widget with defined placeholder text.

    Args:
        placeholder (str): text to be displayed when textbox is empty.
            Defaults to empty.
    """
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFont(Font())


class Combo_Box(QComboBox):
    """A combobox widget with defined items and function to activate when
    an item is selected.

    Args:
        items (list): the options to be contained within the combobox.
            Defaults to empty.
        func (function): the function to run when an item is selected.
            Defaults to None.
    """
    def __init__(self, items=[], func=None):
        super().__init__()
        self.addItems(items)
        if func:
            self.activated.connect(func)
        self.setFont(Font())


class Button(QPushButton):
    """A button widget with defined display text and function to activate when
    clicked.

    Args:
        text (str): text to be displayed within the button. Defaults to empty.
        func (function): function to be run when button is clicked. Defaults to
            None.
    """
    def __init__(self, text="", func=None):
        super().__init__()
        self.setText(text)
        if func:
            self.clicked.connect(func)
        self.setFont(Font())


class RegEx_Validator(QRegularExpressionValidator):
    """A custom regular expression validator that uses the defined regex 
    pattern

    Args:
        pattern (str): the regular expression pattern to be used for validation.
    """
    def __init__(self, pattern):
        re = QRegularExpression(pattern)
        super().__init__(re)
