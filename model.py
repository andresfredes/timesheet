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

import os, sqlite3
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime as dt

from config import DATA_DIR, DB_FILENAME, COLUMN_NAMES

class Model(QSqlTableModel):
    def __init__(self, database):
        super().__init__(db=database)
        try:
            os.mkdir(DATA_DIR)
        except FileExistsError:
            pass
        self._connect()
        self.db.execute(
            'create table if not exists timesheet'
            '(id integer primary key, '
            'task text, '
            'project text, '
            'notes text, '
            'time_in timestamp, '
            'time_out timestamp)'
        )
        self.setTable('timesheet')
        self.setEditStrategy(QSqlTableModel.OnManualChange)
        self.select()
        self.db_cols = {}
        for index, name in enumerate(COLUMN_NAMES):
            self.db_cols[name] = index
            self.setHeaderData(index, Qt.Horizontal, name)

    def _connect(self):
        self.db = sqlite3.connect(
            DATA_DIR + DB_FILENAME,
            detect_types=(sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        )
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()

    def add(self, task, project, notes):
        now = dt.now()
        active = dt.min
        with self.db:
            self.db.execute(
                'insert into timesheet'
                '(task, project, notes, time_in, time_out) '
                'values (?, ?, ?, ?, ?)',
                (task, project, notes, now, active)
            )
        self.submitAll()

    def set_time_out(self, notes):
        now = dt.now()
        active = dt.min
        with self.db:
            self.db.execute(
                'update timesheet '
                'set notes=(?), time_out=(?) '
                'where time_out=(?)',
                (notes, now, active)
            )
        self.submitAll()

    def tasks_projects(self):
        tasks = set()
        projects = set()
        for row in self.db.execute(
            'select all task, project from timesheet'
        ):
            if row:
                tasks.add(row['task'])
                projects.add(row['project'])
        return sorted(tasks), sorted(projects)

    def current_task_project(self):
        active = dt.min
        cursor = self.db.execute(
            'select all task, project, notes, time_in from timesheet '
            'where time_out=(?)',
            (active, )
        )
        current_row = cursor.fetchone()
        format = "%A  %d/%m/%y  %H:%M"
        if current_row:
            return (
                current_row['task'],
                current_row['project'],
                current_row['notes'],
                current_row['time_in'].strftime(format)
            )
        else:
            return None

    def flags(self, index):
        if index.column() == 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.DisplayRole:
            record = QSqlTableModel.data(self, index, role)
            if index.column() in [4, 5]:
                if "0001" in record:
                    return "Running..."
                format = "%Y-%m-%d %H:%M:%S.%f"
                time = dt.strptime(record, format)
                out_format = "%H:%M  %d/%m/%y"
                record = time.strftime(out_format)
            return record
        else:
            return None