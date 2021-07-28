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

from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QTableView, QVBoxLayout,
                             QWidget)

from config import WINDOW
from custom_widgets import (Action, Label, RegExValidator, TextBox, ComboBox,
                            Button)
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
        layout.addLayout(history)

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
        self.model = model
        self.addStretch(1)

        tasks, projects = model.tasks_projects()
        self.task_box = Textbox_with_Combo(self, "Task", tasks)
        self.addLayout(self.task_box)
        self.project_box = Textbox_with_Combo(self, "Project", projects)
        self.addLayout(self.project_box)

        notes_box_layout = QHBoxLayout()
        notes_label = Label(text="Notes (Optional):")
        notes_box_layout.addWidget(notes_label)
        self.notes_box = TextBox(placeholder="Enter Notes")
        notes_box_layout.addWidget(self.notes_box)
        self.addLayout(notes_box_layout)

        self.button = Button(text="Clock In", func=self.clock_in)
        self.button.setEnabled(False)
        self.addWidget(self.button)

        self.addStretch(1)

    def clock_in(self):
        if self.fields_set():
            task = self.task_box.text_box.text()
            project = self.project_box.text_box.text()
            notes = self.notes_box.text()
            self.model.add(task, project, notes)
        else:
            self.task_box.indicate_required()
            self.project_box.indicate_required()

    def text_update(self):
        self.button.setEnabled(self.fields_set())

    def fields_set(self):
        return (self.task_box.text_box.hasAcceptableInput() and
                self.project_box.text_box.hasAcceptableInput())


class Textbox_with_Combo(QHBoxLayout):
    def __init__(self, parent, item_type, items):
        super().__init__()
        self.parent = parent
        label = Label(text=item_type + ":")
        self.addWidget(label)
        self.text_box = TextBox(placeholder="Enter " + item_type + " Name")
        pattern = "^\S.*$"
        # Have at least one non-whitespace, then anything
        re = RegExValidator(pattern)
        self.text_box.setValidator(re)
        self.text_box.textChanged.connect(self.changed)
        self.addWidget(self.text_box)
        or_label = Label(text="OR")
        self.addWidget(or_label)
        combo = ComboBox(items)
        self.addWidget(combo)

    def changed(self):
        self.text_box.setStyleSheet('')
        if self.text_box.hasAcceptableInput():
            self.parent.text_update()

    def indicate_required(self):
        if not self.text_box.hasAcceptableInput():
            self.text_box.setStyleSheet('background-color:red')


class History(QVBoxLayout):
    def __init__(self, model):
        super().__init__()
        label = Label(text="History")
        self.addWidget(label)

        table = QTableView()
        table.setModel(model)
        self.addWidget(table)


class Clock_Out(QVBoxLayout):
    def __init__(self):
        pass