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
from datetime import datetime as dt

from config import DATA_DIR

class Model(QSqlTableModel):
    def __init__(self):
        super(Model, self).__init__()
        try:
            os.mkdir(DATA_DIR)
            self._create()
        except FileExistsError:
            self._connect()

    def _create(self):
        self._connect()
        self.db.execute(
            'create table timesheet'
            '(id integer primary key, '
            'task text, '
            'project text, '
            'notes text, '
            'time_in timestamp, '
            'time_out timestamp)'
        )
        self.db.commit()

    def _connect(self):
        self.db = sqlite3.connect(DATA_DIR + 'data.db')
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()

    def add(self, task, project, notes=""):
        now = dt.now()
        placeholder = dt.min
        with self.db:
            self.db.execute(
                'insert into timesheet'
                '(task, project, notes, time_in, time_out) '
                'values (?, ?, ?, ?, ?)',
                (task, project, notes, now, placeholder)
            )

    def set_time_out(self):
        now = dt.now()
        placeholder = dt.min
        with self.db:
            self.db.execute(
                'update timestamp '
                'set time_out=(?) '
                'where time_out=(?)',
                (now, placeholder)
            )

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
