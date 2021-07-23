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

from PyQt5.QtWidgets import QMainWindow

from config import WINDOW
from custom_widgets import *

class UI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_UI()

    def init_UI(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(
            WINDOW["XPOS"],
            WINDOW["YPOS"],
            WINDOW["WIDTH"],
            WINDOW["HEIGHT"]
        )
        self.add_menu()
        self.add_widgets()

    def add_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        exit_option = Action(
            name='Exit',
            window=self,
            shortcut='Ctrl+Q',
            tip='Exit Program',
            func=self.close
        )
        file_menu.addAction(exit_option)

    def add_widgets(self):
        pass

    def close(self):
        super().close()