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

from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QTableView, QVBoxLayout, QWidget

from config import WINDOW
from custom_widgets import (Action, Label, TextBox, ComboBox, Button)
from model import Model

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Time Tracker"
        self.model = Model()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle(self.title)
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
        self.central = QWidget()
        layout = QHBoxLayout()

        clocker = Task_Clocker(self.model)
        layout.addLayout(clocker)
        history = History(self.model)
        layout.addLayout(recent)

        self.central.setLayout(layout)
        self.setCentralWidget(self.central)

    def refresh_UI(self):
        self.central.setParent(None)
        self.add_widgets()

    def close(self):
        self.model.db.close()
        super().close()


class Task_Clocker(QVBoxLayout):
    def __init__(self, model):
        super().__init__()

        self.addStretch(1)
        
        hbox1 = QHBoxLayout()
        task_label = Label(text="Task:")
        hbox1.addWidget(task_label)
        text_box = TextBox(placeholder="Enter Task Name")
        hbox1.addWidget(text_box)
        or_label = Label(text="OR")
        hbox1.addWidget(or_label)
        combo = ComboBox()
        hbox1.addWidget(combo)
        self.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        project_label = Label(text="Project:")
        hbox2.addWidget(project_label)
        text_box2 = TextBox(placeholder="Enter Project Name")
        hbox2.addWidget(text_box2)
        or_label2 = Label(text="OR")
        hbox2.addWidget(or_label2)
        combo2 = ComboBox()
        hbox2.addWidget(combo2)
        self.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        notes_label = Label(text="Notes (Optional):")
        hbox3.addWidget(notes_label)
        text_box3 = TextBox(placeholder="Enter Notes")
        hbox3.addWidget(text_box3)
        self.addLayout(hbox3)

        button = Button(text="Clock In")
        self.addWidget(button)

        self.addStretch(1)


class History(QVBoxLayout):
    def __init__(self, model):
        super().__init__()
        label = Label(text="History")
        self.addWidget(label)

        table = QTableView()
        table.setModel(model)
        self.addWidget(table)
    