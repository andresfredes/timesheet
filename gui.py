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

gui.py manages the graphical user interface of the timesheet program.
"""

from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QTableView, QVBoxLayout,
                             QWidget, QHeaderView)
from custom_widgets import (Action, Label, RegEx_Validator, Text_Box, Combo_Box,
                            Button)
from model import Model, Database, Empty_DB_Exception
from config import WINDOW, DATA_DIR, DB_FILENAME

class UI(QMainWindow):
    """UI subclasses QMainWindow to produce the window and overall GUI.
    It has been written to conform to Qt's model/view architecture and is
    intended to connect to a QSqlTableModel which manages the database
    interaction. It is built using PyQt5 elements, many of which have been
    subclassed in 'custom_widgets.py'
    """
    def __init__(self):
        super().__init__()
        self.title = "Time Tracker"
        self._init_DB()
        self._init_UI()

    def _init_DB(self):
        db = Database(DATA_DIR + DB_FILENAME)
        db.open()
        self.model = Model(db)

    def _init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(
            WINDOW["XPOS"],
            WINDOW["YPOS"],
            WINDOW["WIDTH"],
            WINDOW["HEIGHT"]
        )
        self._add_menu()
        self._add_widgets()

    def _add_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        exit_option = Action(
            name='Exit',
            window=self,
            shortcut='Ctrl+Q',
            tip='Exit Program',
            func=self._close
        )
        file_menu.addAction(exit_option)

    def _add_widgets(self):
        self.central = QWidget()
        layout = QHBoxLayout()

        if self.model.current_task_project():
            clocker = Clock_Out(self, self.model)
        else:
            clocker = Task_Clocker(self, self.model)
        layout.addLayout(clocker)
        
        self.history = History(self.model)
        layout.addLayout(self.history)
        
        layout.addLayout(Totals_Box(self.model))

        self.central.setLayout(layout)
        self.setCentralWidget(self.central)

    def refresh_UI(self):
        """Clears all of the existing widgets within the UI and refreshes them,
        ensuring that the correct ones are instantiated based on the state.

        <widget>.setParent(None) is Qt's way of deleting widgets, and so
        deleting the central widget causes deletions to cascade down the 
        parent-child chain until the UI is clear.
        """
        self.central.setParent(None)
        self._add_widgets()

    def _close(self):
        super().close()

    def closeEvent(self, event):
        """This is an overridden function from QMainWindow that will trigger
        in the event of the window being closed. This ensures that the
        database in the associated model is always closed safely.
        This function is part of the default functionality of a Qt View and
        does not require direct calling.

        Args:
            event (QCloseEvent): This is automatically passed when the window is
                closed.
        """
        self.model.db.close()


class Task_Clocker(QVBoxLayout):
    """This is a subclassed QVBoxLayout, designed to hold a group of widgets
    that will work together to produce the 'Task Clocker' part of the program.
    It provides the user with the textboxes and button to enter and then save
    their task information.

    This section of the UI will be swapped with Clock_Out widget, depending on
    whether there is a currently running task.

    Args:
        parent (QMainWindow): window widget that the Task_Clocker will be
            instantiated within.
        model (QSqlTableModel): model that handles the saving and returning of
            database information.
    """
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
        
        self.button = Button(text="Clock In", func=self._clock_in)
        self.button.setEnabled(False)
        self.addWidget(self.button)

        self.addStretch(2)

    def _clock_in(self):
        if self.fields_set():
            task = self.task_box.text_box.text()
            project = self.project_box.text_box.text()
            notes = self.notes_box.text_box.text()
            self.model.add(task, project, notes)
            self.parent.refresh_UI()
        else:
            self.task_box._indicate_required()
            self.project_box._indicate_required()

    def _text_update(self):
        self.button.setEnabled(self._fields_set())

    def _fields_set(self):
        return (self.task_box.text_box.hasAcceptableInput() and
                self.project_box.text_box.hasAcceptableInput())


class Textbox_with_Combo(QHBoxLayout):
    """This is a subclassed QHBoxLayout, designed to be inserted into a larger
    UI. It bundles together a label, textbox and combobox along with the
    functionality to know when correct data has been either input into the
    text-box or selected from the combobox.

    Args:
        parent (QMainWindow): window widget that this object will be
            instantiated within.
        item_type (str): the type of information to list on the label.
        items (list): the options that will be presented in the combobox
    """
    def __init__(self, parent, item_type, items):
        super().__init__()
        self.parent = parent
        label = Label(text=f"{item_type}:")
        self.addWidget(label)
        self.text_box = Text_Box(placeholder=f"Enter {item_type} Name")
        pattern = "^\S.*$"
        # Have at least one non-whitespace, then anything
        re = RegEx_Validator(pattern)
        self.text_box.setValidator(re)
        self.text_box.textChanged.connect(self._changed)
        self.addWidget(self.text_box)
        or_label = Label(text="OR")
        self.addWidget(or_label)
        combo = Combo_Box(items)
        self.addWidget(combo)

    def _changed(self):
        self.text_box.setStyleSheet('')
        if self.text_box.hasAcceptableInput():
            self.parent._text_update()

    def _indicate_required(self):
        if not self.text_box.hasAcceptableInput():
            self.text_box.setStyleSheet('background-color:red')


class Notes_Box(QHBoxLayout):
    """This is a subclassed QHBoxLayout, designed to be inserted into a larger
    UI. It bundles together a label with a textbox, but allows for the textbox
    to be filled on creation.

    Args:
        notes (str): The string to pre-fill the textbox with. Defaults to empty.
    """
    def __init__(self, notes=""):
        super().__init__()
        notes_label = Label(text="Notes (Optional):")
        self.addWidget(notes_label)
        self.text_box = Text_Box(placeholder="Enter Notes")
        if notes:
            self.text_box.setText(notes)
        self.addWidget(self.text_box)


class History(QVBoxLayout):
    """This is a subclassed QVBoxLayout used as a container for a QTableView
    that will be the user's primary way of viewing information from the attached
    database model.

    Args:
        model (QSqlTableModel): The data model to be viewed.
    """
    def __init__(self, model):
        super().__init__()
        self.model = model
        label = Label(text="History")
        self.addWidget(label)
        self.table = QTableView()
        self._init_table()

    def _init_table(self):
        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.addWidget(self.table)


class Clock_Out(QVBoxLayout):
    """This is a subclassed QVBoxLayout designed to hold the group of widgets
    that will allows a user to view the currently running task and 'clock out'.
    It provides a textbox to allow the user to update their notes and button to
    submit.

    This section of the UI will be swapped with Task_Clocker widget, depending
    on whether there is a currently running task.
    
    Args:
        parent (QMainWindow): window widget that this object will be
            instantiated within.
        model (QSqlTableModel): model that handles the saving and returning of
            database information.
    """
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

        button = Button(text="Clock Out", func=self._clock_out)
        self.addWidget(button)

        self.addStretch(2)

    def _clock_out(self):
        notes = self.notes_box.text_box.text()
        self.model.set_time_out(notes)
        self.parent.refresh_UI()

class Totals_Box(QVBoxLayout):
    """This is a subclassed QVBoxLayout designed to hold the group of widgets
    that will present the total elapsed time of the most recent (or active)
    task and project. All contained widgets are information bearing only, so
    does not invite any user interaction.

    Args:
        model (QSqlTableModel): the data model to source the time data from.
    """
    def __init__(self, model):
        super().__init__()
        self.model = model
        title = Label(text="Totals")
        self.addWidget(title)
        self.addStretch(1)

        try:
            task, project = self.model.most_recent()
        except Empty_DB_Exception:
            label = Label(text="No timesheet details saved")
            self.addWidget(label)
        else:
            task_week, task_total = self.model.get_total_time("task", task)
            project_week, project_total = self.model.get_total_time(
                "project", project)
            totals_list = self._format_labels(task, task_week, task_total)
            totals_list.extend(
                self._format_labels(project, project_week, project_total)
            )
            for text in totals_list:
                style = "bold" if text in totals_list[::2] else ""
                new_label = Label(text=text, style=style)
                self.addWidget(new_label)
        self.addStretch(1)

    def _format_labels(self, item, week, total):
        return [
            f"{item} this week",
            f"{self._format_time(week)}",
            f"{item} total",
            f"{self._format_time(total)}"
        ]

    def _format_time(self, time):
        days = time.days
        hours = time.seconds // 3600
        day_string = f"Days: {days} " if days else ""
        return f"{day_string}Hours: {hours}"