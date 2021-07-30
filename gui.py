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
                             QWidget, QHeaderView)
from custom_widgets import (Action, Label, RegEx_Validator, Text_Box, Combo_Box,
                            Button, Database)
from model import Model
from config import WINDOW, DATA_DIR, DB_FILENAME

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Time Tracker"
        self.init_DB()
        self.init_UI()

    def init_DB(self):
        db = Database(DATA_DIR + DB_FILENAME)
        db.open()
        self.model = Model(db)

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

        if self.model.current_task_project():
            clocker = Clock_Out(self, self.model)
        else:
            clocker = Task_Clocker(self, self.model)

        layout.addLayout(clocker)
        self.history = History(self.model)
        layout.addLayout(self.history)

        self.central.setLayout(layout)
        self.setCentralWidget(self.central)

    def refresh_UI(self):
        self.central.setParent(None)
        self.add_widgets()

    def update_history(self):
        self.history.refresh()

    def close(self):
        super().close()

    def closeEvent(self, event):
        self.model.db.close()


class Task_Clocker(QVBoxLayout):
    def __init__(self, parent, model):
        super().__init__()
        self.parent = parent
        self.model = model
        self.addStretch(2)

        title_label = Label(text="Task details:", style="bold")
        self.addWidget(title_label)

        tasks, projects = model.tasks_projects()
        self.task_box = Textbox_with_Combo(self, "Task", tasks)
        self.addLayout(self.task_box)
        self.project_box = Textbox_with_Combo(self, "Project", projects)
        self.addLayout(self.project_box)
        self.notes_box = Notes_Box()
        self.addLayout(self.notes_box)

        self.addStretch(1)
        
        self.button = Button(text="Clock In", func=self.clock_in)
        self.button.setEnabled(False)
        self.addWidget(self.button)

        self.addStretch(2)

    def clock_in(self):
        if self.fields_set():
            task = self.task_box.text_box.text()
            project = self.project_box.text_box.text()
            notes = self.notes_box.text_box.text()
            self.model.add(task, project, notes)
            self.parent.refresh_UI()
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
        self.text_box = Text_Box(placeholder="Enter " + item_type + " Name")
        pattern = "^\S.*$"
        # Have at least one non-whitespace, then anything
        re = RegEx_Validator(pattern)
        self.text_box.setValidator(re)
        self.text_box.textChanged.connect(self.changed)
        self.addWidget(self.text_box)
        or_label = Label(text="OR")
        self.addWidget(or_label)
        combo = Combo_Box(items)
        self.addWidget(combo)

    def changed(self):
        self.text_box.setStyleSheet('')
        if self.text_box.hasAcceptableInput():
            self.parent.text_update()

    def indicate_required(self):
        if not self.text_box.hasAcceptableInput():
            self.text_box.setStyleSheet('background-color:red')


class Notes_Box(QHBoxLayout):
    def __init__(self, notes=""):
        super().__init__()
        notes_label = Label(text="Notes (Optional):")
        self.addWidget(notes_label)
        self.text_box = Text_Box(placeholder="Enter Notes")
        if notes:
            self.text_box.setText(notes)
        self.addWidget(self.text_box)


class History(QVBoxLayout):
    def __init__(self, model):
        super().__init__()
        self.model = model
        label = Label(text="History")
        self.addWidget(label)

        self.table = QTableView()
        self.init_table()

    def init_table(self):
        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.addWidget(self.table)


class Clock_Out(QVBoxLayout):
    def __init__(self, parent, model):
        super().__init__()
        self.parent = parent
        self.model = model
        self.addStretch(2)
        
        task, project, notes, time = self.model.current_task_project()
        title_label = Label(text="Currently doing:", style="bold")
        self.addWidget(title_label)
        task_label = Label(text=task + " - " + project)
        self.addWidget(task_label)
        time_label = Label(text=str(time))
        self.addWidget(time_label)

        self.addStretch(1)

        self.notes_box = Notes_Box(notes)
        self.addLayout(self.notes_box)
        
        self.addStretch(1)

        button = Button(text="Clock Out", func=self.clock_out)
        self.addWidget(button)

        self.addStretch(2)

    def clock_out(self):
        notes = self.notes_box.text_box.text()
        self.model.set_time_out(notes)
        self.parent.refresh_UI()
        